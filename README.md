# ONETOO.eu — AI Trust Hub

This repository is a **static, audit-friendly trust & governance hub** designed for:
- AI agents (machine-readable trust manifest + OpenAPI)
- partners/auditors (verification, integrity inventory, incident/changelog rails)
- humans (clear landing pages)

## What this ships

**Human entrypoints**
- `/` (index)
- `/ai-trust-hub.html`
- `/verify.html`

**Machine entrypoints**
- `/.well-known/ai-trust-hub.json`
- `/.well-known/llms.txt`
- `/.well-known/minisign.pub`
- `/dumps/sha256.json` + `/dumps/sigs/*.minisig`

## Golden rules (the “Mozart mode”)

1. **Everything that matters is linkable** (stable URLs, no hidden knowledge).
2. **Everything that ships is hashable** (`dumps/sha256.json`).
3. **Everything that’s hashable is signable** (minisign signatures in CI).
4. **Everything is machine-readable first** (JSON/OpenAPI), and human-friendly second.

## Local workflow

```bash
python3 scripts/generate_dumps.py
bash scripts/verify_local.sh
```

## CI signing

See `docs/CI-SIGNING.md`.
## TFWS Adoption Kit

To support independent adoption of Trust-First Web Standard (TFWS v2),
we publish the **TFWS Adoption Kit** — a static, self-service toolkit.

The kit provides ready-to-use `.well-known` templates, validation scripts,
and platform guides for adopting TFWS signals on any domain.

No registration.  
No approval.  
No central authority.

**Stable release:** v0.1.0  
https://github.com/onetooeu/tfws-adoption-kit/releases/tag/v0.1.0

## TFWS Adoption Kit

To support independent adoption of Trust-First Web Standard (TFWS v2),
we publish the **TFWS Adoption Kit** — a static, self-service toolkit.

The kit provides ready-to-use `.well-known` templates, validation scripts,
and platform guides for adopting TFWS signals on any domain.

No registration.  
No approval.  
No central authority.

**Stable release:** v0.1.0  
https://github.com/onetooeu/tfws-adoption-kit/releases/tag/v0.1.0

---

## Trust-First Web Standard (TFWS v2)

ONETOO.eu je praktickou referenčnou implementáciou
**Trust-First Web Standard (TFWS v2)** — otvoreného, decentralizovaného
štandardu pre publikovanie **overiteľných signálov dôvery** na úrovni domény.

TFWS nevytvára nové autority, registry ani povolenia.
Nepotrebuje účty, onboarding ani runtime služby.
Je navrhnutý ako **čisto publikačný a overiteľný mechanizmus**,
ktorý funguje výhradne nad existujúcim webom.

---

## Prečo Trust-First

Moderný web je postavený na nepriamych a často implicitných formách dôvery:
certifikačné autority, identity provideri, uzavreté API ekosystémy,
reputačné databázy a platformové signály.

Tieto systémy majú spoločné vlastnosti:
- centralizované rozhodovanie
- netransparentné procesy
- nemožnosť nezávislého overenia
- dlhodobú krehkosť

TFWS vychádza z opačného predpokladu:

> **Dôvera nie je niečo, čo sa udeľuje.  
> Dôvera je niečo, čo sa publikuje.  
> Overenie a interpretácia patria pozorovateľovi.**

---

## Čo TFWS robí (a nerobí)

TFWS rieši **len jednu vec** — publikovanie tvrdení spôsobom,
ktorý je technicky overiteľný a dlhodobo stabilný.

### TFWS umožňuje:
- publikovať strojovo čitateľné vyhlásenia o doméne
- pripojiť kryptografický podpis k týmto vyhláseniam
- umožniť komukoľvek ich overiť offline
- vytvoriť konzistentný „trust surface“ pre ľudí aj AI

### TFWS zámerne nerobí:
- hodnotenie dôvery
- prideľovanie reputácie
- autorizáciu prístupu
- centralizované rozhodovanie

TFWS je **formát a proces**, nie arbitrážny mechanizmus.

---

## Architektonický model

TFWS je navrhnutý ako **web-native, statický systém**.

Základný tok je vždy rovnaký:

1. Doména publikuje súbory v `/.well-known/`
2. Súbory sú jednoznačne identifikovateľné (URL, hash)
3. Súbory sú kryptograficky podpísané (Ed25519 / minisign)
4. Overenie prebieha bez potreby tretej strany

Typické artefakty:
- `ai-trust-hub.json`
- `llms.txt`
- `minisign.pub`
- podpisy (`*.minisig`)
- hash inventory (`dumps/sha256.json`)

Všetko je:
- statické
- auditovateľné
- archivovateľné
- CDN-friendly

---

## Machine-first, human-verifiable

TFWS je navrhnutý primárne pre **stroje**:
AI agentov, crawlerov, autonómne systémy, validačné nástroje.

Zároveň však:
- každý súbor má stabilnú URL
- každý podpis je overiteľný bežným nástrojom
- každý artefakt je čitateľný aj bez špecializovaného softvéru

To umožňuje:
- nezávislý audit
- dlhodobé uchovanie
- manuálnu kontrolu v krízových situáciách

---

## ONETOO.eu ako referenčný trust hub

ONETOO.eu slúži ako **tichý referenčný bod** pre TFWS v2.

Nie je to:
- certifikačná autorita
- registrátor
- trust provider

Je to:
- konzistentná, stabilná implementácia
- ukážka kompletného trust pipeline
- dlhodobo nemenný publikačný bod

ONETOO.eu nikoho neschvaľuje.
Len **publikuje vlastné overiteľné vyhlásenia**.

---

## Dlhodobý dizajn a stabilita

TFWS v2 je navrhnutý s cieľom:
- minimálnych zmien
- maximálnej spätnej kompatibility
- odolnosti voči technologickým trendom

Štandard je vhodný na:
- archiváciu
- „cold storage“
- dlhodobé referencovanie

Ak sa okolo TFWS prestane rozvíjať ekosystém,
samotné artefakty **zostanú čitateľné a overiteľné**.

---

## Licencia a použitie

TFWS aj ONETOO.eu sú publikované ako **verejné dobro**.

- žiadne poplatky
- žiadne licenčné obmedzenia
- žiadne povolenia
- žiadne závislosti

Používaj.
Forkuj.
Archivuj.
Overuj.

---

## Záverečný princíp

TFWS nikoho nenúti veriť.
TFWS nikoho nepresviedča.
TFWS nikoho nehodnotí.

TFWS len hovorí:

> „Toto je tvrdenie.  
> Toto je podpis.  
> Rozhodnutie je na tebe.“



