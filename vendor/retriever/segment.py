"""Step 3: deterministic segmentation, replacing LLM Pass 1's span extraction.

record -> PRE (drop disposal/origin/section lines, heading rule) -> base units (line, bullet,
sentence end; never a comma) -> footnote join -> 2-unit windows -> dedupe by source_field.

Every emitted span is verbatim: `text` is a slice of the field (leading bullets and trailing
`.`/`;` stripped), plus ` ... <footnote bodies>` when it carries a marker, which matches the
gold `claim_text` format. Settings come from the `pre` and `segmentation` sections of
ecgt_retriever.yaml.

Usage:
  from retriever.segment import load_config, segment_record
  spans = segment_record(record, load_config())
  python3 retriever/segment.py golden/clean/carrefour.json --index 1     # print one record's spans
"""
import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

# Sentence end: [.!?] (plus closing quotes) followed by whitespace and an uppercase/quote/digit start.
_SENT_END = re.compile(r"[.!?]+[\"»”’)]*\s+(?=[A-ZÀ-ÝÈÉ«\"“0-9#])")
# Abbreviations that must not end a sentence: «Dott. Giorgio», «A.I.Nut. Associazione», «S.p.A. Via».
_ABBREV = re.compile(r"(?:\b(?:Dott|Dr|Sig|Sigg|Prof|ecc|es|ca|nr|n|art|pag|tel|Spa|Srl|vs)|\b(?:[A-Za-z]{1,4}\.)+[A-Za-z]{0,4})$")


_LINE_BREAK = re.compile(r"\n|<br\s*/?>", re.I)
_EDGE_TAG_START = re.compile(r"(?:</?[a-z][^>]{0,20}>\s*)+", re.I)
_EDGE_TAG_END = re.compile(r"(?:\s*</?[a-z][^>]{0,20}>)+$", re.I)


def load_config(path=HERE / "ecgt_retriever.yaml"):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


@dataclass
class Span:
    text: str                       # emitted text: verbatim slice, plus " ... " + footnote bodies
    source_field: str
    kind: str                       # "unit" | "window" | "list_item"
    start: int                      # char offsets of the claim part inside the field
    end: int
    footnotes: list = field(default_factory=list)   # joined body lines, in document order
    clauses: list = field(default_factory=list)     # comma sub-clauses, for scoring only
    also_in: list = field(default_factory=list)     # other fields holding the same text


@dataclass
class _Line:
    start: int
    end: int
    text: str
    drop: str | None = None         # PRE reason, or "footnote_body"
    marker: str | None = None       # for footnote body lines


class Segmenter:
    def __init__(self, cfg):
        pre, seg = cfg["pre"], cfg["segmentation"]
        self.text_fields = pre["text_fields"]
        self.drop_lines = {reason: [re.compile(p, re.I) for p in pats]
                           for reason, pats in pre["drop_lines"].items()}
        self.heading_max_words = pre["heading_max_words"]
        self.heading_match = re.compile(pre["heading_match"], re.I)
        self.heading_keep = re.compile(pre["heading_keep"], re.I)
        self.lead = "".join(seg["strip_leading"]) + " \t"
        self.trail = "".join(seg["strip_trailing"]) + " \t"
        self.window_size = seg["window_size"]
        self.markers = sorted(seg["footnote_markers"], key=len, reverse=True)
        self.sep = seg["footnote_join_separator"]
        self.drop_bodies = seg["drop_joined_footnote_bodies"]
        alt = "|".join(re.escape(m) for m in self.markers)
        # A marker inside a claim: right after a non-space char, not followed by a word char,
        # so «N°1» and «12 °C» are not markers.
        self._marker_in = re.compile(rf"(?<=\S)({alt})(?![\w*^°])")

    # ---- lines and PRE -------------------------------------------------------------------

    def _lines(self, text):
        """Split on newlines and HTML <br> (Carrefour), keeping field offsets. Two breaks in a
        row give an empty line, i.e. a paragraph break."""
        out, pos = [], 0
        for m in [*_LINE_BREAK.finditer(text), None]:
            s, e = pos, (m.start() if m else len(text))
            pos = m.end() if m else len(text)
            while True:                 # strip bullets, whitespace and boundary tags (<b>, </b>)
                while s < e and text[s] in self.lead:
                    s += 1
                while e > s and text[e - 1] in " \t\r":
                    e -= 1
                t = _EDGE_TAG_START.match(text, s, e)
                if t:
                    s = t.end()
                    continue
                t = _EDGE_TAG_END.search(text[s:e])
                if t:
                    e = s + t.start()
                    continue
                break
            out.append(_Line(s, e, text[s:e]))
        return out

    def _pre(self, lines):
        for ln in lines:
            if not ln.text:
                continue
            for reason, pats in self.drop_lines.items():
                if any(p.search(ln.text) for p in pats):
                    ln.drop = reason
                    break
        # Heading rule: the line directly above (no blank line between) a pattern-dropped
        # disposal line. No chaining, so text above a heading is never pulled in.
        headings = [ln for ln, nxt in zip(lines, lines[1:])
                    if ln.text and ln.drop is None and nxt.drop == "disposal"
                    and len(ln.text.split()) <= self.heading_max_words
                    and not ln.text.endswith((".", "!", "?"))
                    and self.heading_match.search(ln.text)
                    and not self.heading_keep.search(ln.text)]
        for ln in headings:
            ln.drop = "disposal_heading"
        for ln in lines:
            if ln.drop is None and ln.text:
                m = next((m for m in self.markers if ln.text.startswith(m)), None)
                if m:
                    ln.marker = m
        return lines

    # ---- units --------------------------------------------------------------------------

    def _strip(self, text, s, e):
        while s < e and text[s] in self.lead:
            s += 1
        while e > s and text[e - 1] in self.trail:
            e -= 1
        return s, e

    def _sentences(self, text, ln):
        """Split one kept line at sentence ends, returning (start, end) offsets in the field."""
        cuts, s = [], ln.start
        for m in _SENT_END.finditer(ln.text):
            if _ABBREV.search(ln.text[:m.start()]) and ln.text[m.start()] == ".":
                continue
            cuts.append((s, ln.start + m.end()))
            s = ln.start + m.end()
        cuts.append((s, ln.end))
        return [self._strip(text, a, b) for a, b in cuts]

    def _field_units(self, text):
        """Return (units, bodies). Units are (start, end, line_no); bodies are _Line objects."""
        lines = self._pre(self._lines(text))
        units, bodies = [], []
        for i, ln in enumerate(lines):
            if not ln.text or ln.drop:
                continue
            if ln.marker:
                bodies.append(ln)
                continue
            for a, b in self._sentences(text, ln):
                if b > a:
                    units.append((a, b, i))
        return units, bodies, lines

    # ---- record -------------------------------------------------------------------------

    def segment(self, record):
        fields = {}
        for name in self.text_fields:
            val = record.get(name)
            if isinstance(val, list):
                fields[name] = [str(v) for v in val if str(v).strip()]
            elif isinstance(val, str) and val.strip():
                fields[name] = val

        parsed = {n: self._field_units(t) for n, t in fields.items() if isinstance(t, str)}
        all_bodies = [(n, b) for n, (_, bodies, _) in parsed.items() for b in bodies]
        used_bodies = set()

        def footnotes_for(fname, claim):
            """Bodies for each marker in claim: same field first, else any field."""
            found = {}
            for m in dict.fromkeys(self._marker_in.findall(claim)):
                same = [(n, b) for n, b in all_bodies if n == fname and b.marker == m]
                for n, b in same or [(n, b) for n, b in all_bodies if b.marker == m]:
                    found[id(b)] = (n, b)
                    used_bodies.add(id(b))
            ordered = sorted(found.values(), key=lambda nb: (self.text_fields.index(nb[0]), nb[1].start))
            return [b.text for _, b in ordered]

        spans = []

        def make(fname, kind, a, b, text):
            claim = text[a:b]
            notes = footnotes_for(fname, claim)
            full = claim + (self.sep + "\n".join(notes) if notes else "")
            clauses = [c.strip() for c in claim.split(",") if c.strip()]
            spans.append(Span(full, fname, kind, a, b, notes,
                              clauses if len(clauses) > 1 else [claim]))

        for fname, val in fields.items():
            if isinstance(val, list):
                for item in val:
                    a, b = self._strip(item, 0, len(item))
                    if b > a:
                        make(fname, "list_item", a, b, item)
                continue
            units, _, lines = parsed[fname]
            for a, b, _ in units:
                make(fname, "unit", a, b, val)
            # Windows: consecutive units within one paragraph, never across a blank line, a
            # dropped line or a footnote body.
            for k in range(2, self.window_size + 1):
                for j in range(len(units) - k + 1):
                    grp = units[j:j + k]
                    between = lines[grp[0][2]:grp[-1][2] + 1]
                    if any(not ln.text or ln.drop or ln.marker for ln in between):
                        continue
                    make(fname, "window", grp[0][0], grp[-1][1], val)

        # Unused footnote bodies stay as ordinary units (recall-first).
        for n, b in all_bodies:
            if id(b) not in used_bodies or not self.drop_bodies:
                a, e = self._strip(fields[n], b.start, b.end)
                spans.append(Span(fields[n][a:e], n, "unit", a, e, [], [fields[n][a:e]]))

        return _dedupe(spans, self.text_fields)


def _norm(s):
    """Comparison key: case, whitespace and the stripped trailing punctuation (also before a
    footnote join) don't count."""
    s = re.sub(r"\s+", " ", s).strip().lower()
    s = re.sub(r"[.;!?]+(?= \.\.\. )", "", s)
    return s.rstrip(".;!?").strip()


def _dedupe(spans, priority):
    best = {}
    for sp in spans:
        key = _norm(sp.text)
        cur = best.get(key)
        if cur is None:
            best[key] = sp
        elif priority.index(sp.source_field) < priority.index(cur.source_field):
            sp.also_in = sorted(set(cur.also_in + [cur.source_field]) - {sp.source_field})
            best[key] = sp
        elif sp.source_field != cur.source_field and sp.source_field not in cur.also_in:
            cur.also_in.append(sp.source_field)
    return list(best.values())


_SEGMENTER = {}


def segment_record(record, cfg=None):
    cfg = cfg or load_config()
    seg = _SEGMENTER.get(id(cfg))
    if seg is None:
        seg = _SEGMENTER[id(cfg)] = Segmenter(cfg)
    return seg.segment(record)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("records", help="JSON list of product records")
    ap.add_argument("--index", type=int, default=0)
    args = ap.parse_args()
    rec = json.load(open(args.records, encoding="utf-8"))[args.index]
    for sp in segment_record(rec):
        tag = f"{sp.source_field}/{sp.kind}" + (f" +{','.join(sp.also_in)}" if sp.also_in else "")
        print(f"[{tag}] {sp.text!r}")


if __name__ == "__main__":
    main()
