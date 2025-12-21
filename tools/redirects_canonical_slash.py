from pathlib import Path

LANGS = ["bg","cs","da","de","el","en","es","et","fi","fr","ga","hr","hu","it","lt","lv","mt","nl","pl","pt","ro","sk","sl","sv"]
PAGES = ["for-humans","for-businesses","for-ai","about","pricing","partners","affiliate","methodology","incidents","regulatory","transparency"]

existing = Path("_redirects").read_text(encoding="utf-8").splitlines()

out = []
seen = set()

def add(line):
    if line not in seen:
        out.append(line)
        seen.add(line)

# zachovaj pôvodné všeobecné pravidlá (nie i18n)
for line in existing:
    s = line.strip()
    if not s or s.startswith("#"):
        add(line)
        continue
    if any(s.startswith(f"/{l}/") or s.startswith(f"/{l} ") for l in LANGS):
        continue
    if any(s.startswith(f"/{p}") for p in PAGES):
        continue
    add(line)

add("")
add("# root convenience routes")
for p in PAGES:
    add(f"/{p} /en/{p}/ 302")

add("")
add("# i18n canonical trailing slash")
for l in LANGS:
    add(f"/{l} /{l}/ 301")
    add(f"/{l}/ /{l}/index.html 200")
    for p in PAGES:
        add(f"/{l}/{p} /{l}/{p}/ 301")
        add(f"/{l}/{p}/ /{l}/{p}/index.html 200")

add("")
add("# optional: .html -> slash")
for l in LANGS:
    for p in PAGES:
        add(f"/{l}/{p}.html /{l}/{p}/ 301")

Path("_redirects").write_text("\n".join(out) + "\n", encoding="utf-8")
print("OK: canonical trailing-slash redirects generated")
