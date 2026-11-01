from bs4 import BeautifulSoup
import re
import json

with open('./UCPD.html', 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

def clean(text):
    return re.sub(r'\s+', ' ', text).strip()

chunks = []

# --- 1. New definitions from Art 1, section 1b (letters o-w) ---
# These are the greenwashing-specific new terms added to UCPD Art 2.
# Each letter (o, p, q, r, s, t, u, v, w) becomes its own chunk instead of
# one chunk covering all 9 definitions — a single combined chunk is an
# over-broad match magnet in retrieval (every query about any one of these
# terms matches the whole block).
art1 = soup.find(id='art_1')
art1_text = clean(art1.get_text())

DEFINITION_TITLES = {
    'o': '"asserzione ambientale"',
    'p': '"asserzione ambientale generica"',
    'q': '"marchio di sostenibilità"',
    'r': '"sistema di certificazione"',
    's': '"eccellenza riconosciuta delle prestazioni ambientali"',
    't': '"durabilità"',
    'u': '"aggiornamento del software"',
    'v': '"materiali di consumo"',
    'w': '"funzionalità"',
}

# find the table row with "b)" which contains the new letters o-w
tables = art1.find_all('table')
for tbl in tables:
    cells = tbl.find_all('td')
    if len(cells) >= 2:
        label = clean(cells[0].get_text())
        content = clean(cells[1].get_text())
        if label == 'b)' and 'asserzione ambientale' in content:
            # Split the combined insertion text into one segment per
            # lettered definition. Sub-items (i, ii, iii, iv under "r")
            # and footnote markers use roman numerals / "(*n)", not a
            # bare "<letter>) <quote>", so they don't false-split here.
            letter_pattern = re.compile(r'([opqrstuvw])\)\s+[“"]')
            matches = list(letter_pattern.finditer(content))
            segs = {}
            for i, m in enumerate(matches):
                letter = m.group(1)
                start = m.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                segs[letter] = content[start:end].strip().rstrip(';').strip()

            # Footnotes referenced from "s" and "u" ((*2), (*3)) are
            # dumped in the source HTML at the very end of the whole
            # insertion (after "w"), not next to the definition that
            # cites them. Move each footnote's text onto its own
            # definition instead of leaving both stuck onto "w".
            footnote_match = re.search(
                r'^(.*?)\s*(\(\*2\).*?pag\.\s*1\)\.)["»]?\s*(\(\*3\).*?pag\.\s*1\)\.)["»]?\.?$',
                segs.get('w', ''), re.DOTALL
            )
            if footnote_match:
                segs['w'] = footnote_match.group(1).strip()
                segs['s'] = segs['s'] + '. ' + footnote_match.group(2).strip()
                segs['u'] = segs['u'] + '. ' + footnote_match.group(3).strip()

            for letter in ['o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w']:
                if letter not in segs:
                    continue
                chunks.append({
                    "id": f"ECGT_Art1_NuoveDefinizioni_{letter}",
                    "title": f"ECGT Art. 1, lett. {letter}) – Definizione di {DEFINITION_TITLES[letter]}",
                    "source": "art_1",
                    "text": f"ECGT Articolo 1 – Nuova definizione inserita nella direttiva 2005/29/CE: «{segs[letter]}»."
                })
            break

# --- 2. Annex items – new blacklist entries ---
print("Processing Annex I items...")
anx = soup.find(id='anx_1')

# The annex has outer tables (numbered 1-4) each inserting one or more inner items
# Inner items have labels like "2 bis)", "4 bis)", etc.
# We want each inner item as its own chunk

def get_inner_items(container):
    items = []
    for tbl in container.find_all('table', recursive=True):
        rows = tbl.find_all('tr', recursive=False)
        for row in rows:
            cells = row.find_all('td', recursive=False)
            if len(cells) < 2:
                continue
            label = clean(cells[0].get_text())
            content = clean(cells[1].get_text())
            # match labels like "2 bis)", "4 bis)", "4 ter)", "10 bis)", "23 quinquies)" etc.
            if re.match(r'^\d+\s+\w+\)$', label) or re.match(r'^\d+\s+\w+\s+\w+\)$', label):
                item_id = label.rstrip(')').replace(' ', '_')
                items.append((label, content, item_id))
    return items

inner = get_inner_items(anx)
print(f"Found {len(inner)} inner items in Annex I.")
for label, content, item_id in inner:
    # strip trailing footnote markers and quotes
    content = content.strip('»').strip('«').strip(';').strip()
    chunks.append({
        "id": f"ECGT_AnnexI_{item_id}",
        "title": f"ECGT Allegato – nuovo punto {label} (inserito in Allegato I UCPD)",
        "source": "anx_1",
        "text": f"ECGT Allegato I – punto {label}: {content}"
    })

print(f"Total chunks: {len(chunks)}")
for c in chunks:
    print(c['id'])
    print(c['text'][:200])
    print()

with open('ecgt_chunks.json', 'w', encoding='utf-8') as f:
    json.dump(chunks, f, ensure_ascii=False, indent=2)
