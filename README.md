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

Ďakujem. Toto beriem ako **definitívne uzavretie fázy „Autopilot activation“**.
Nižšie máš **kompletný, systematický, archívny report** – písaný ako **„technická Biblia“**, aby si ho vedel **uložiť, archivovať, zdieľať s AI agentmi** a vrátiť sa k nemu aj o roky.

---

# 📘 **ONETOO Autopilot – Final Activation Report**

**Stav:** uzavreté
**Dátum:** 11. 01. 2026
**Projekt:** **ONETOO**

---

## 1️⃣ ČO SME DNES SKUTOČNE AKTIVOVALI

Dnes sa projekt **ONETOO** posunul z *manuálne spravovaného trust-registry* do stavu:

> 🧠 **Autonómny, samoriadiaci, deterministický AI trust systém**

Konkrétne sme **aktivovali a stabilizovali**:

### ✅ ONETOO Autopilot (produkčný režim)

* automatické spracovanie **pending → sandbox → accepted**
* deterministické rozhodovanie (žiadna náhoda, žiadny ML black-box)
* plne auditovateľné rozhodnutia
* bezpečné zlyhanie (fail-safe)

### ✅ Stabilný trust-root

* `contrib-accepted.json` je:

  * kanonizovaný
  * deduplikovaný
  * **kryptograficky podpísaný (minisign)**
* `ai-search-index.json` správne ukazuje na signed accepted-set

### ✅ Produkčné prepojenie

* **search.onetoo.eu** (submission API)
* **[www.onetoo.eu](http://www.onetoo.eu)** (trust-root + public dumps)
* **Cloudflare Pages** (globálna distribúcia)

---

## 2️⃣ ARCHITEKTÚRA AUTOPILOTA (STRUČNE, ALE PRESNE)

```
Publisher → /contrib/v2/pending
              ↓
        Autopilot Runner
              ↓
   ┌────────────┬─────────────┬──────────────┐
   │  reject    │   sandbox   │   accepted   │
   └────────────┴─────────────┴──────────────┘
              ↓
     signed accepted-set
              ↓
      AI Search Registry
```

Autopilot **nikdy nepíše priamo do indexu**.
Index je len **pointer** na kryptograficky overiteľné dáta.

---

## 3️⃣ ROZHODOVACÍ MODEL – AKO AUTOPILOT „MYSLÍ“

### 3.1 Hard-fail pravidlá (absolútne)

Tieto pravidlá **okamžite vyradia** záznam:

* ❌ ne-HTTPS URL
* ❌ `file:`, `data:`, `javascript:` schémy
* ❌ `localhost`, `127.0.0.1`, privátne IP

➡️ **Žiadne výnimky.**

---

### 3.2 Soft-rules (bodové hodnotenie)

Každý publisher dostáva **score 0–100**.

| Signál                  | Body    |
| ----------------------- | ------- |
| `.well-known/` existuje | +10     |
| `.well-known` HTTP 200  | +15     |
| `minisign.pub`          | +10     |
| `sha256.json`           | +10     |
| **TFWS minimal bundle** | **+10** |
| `security.txt`          | +5      |
| GitHub repo             | +5      |
| allowlist host          | +20     |

---

### 3.3 Nový signál: **tfws_min_bundle**

> 🔑 **Kľúčová dnešná zmena**

```text
tfws_min_bundle = minisign.pub AND sha256.json
```

Význam:

* publisher **chápe kryptografickú zodpovednosť**
* vie publikovať overiteľné artefakty
* je pripravený na AI-trust ekosystém

➡️ Takýto publisher je **preferovaný**.

---

## 4️⃣ PRAHOVÉ HODNOTY (FINÁLNE)

| Stav         | Podmienka |
| ------------ | --------- |
| **reject**   | < 10      |
| **sandbox**  | ≥ 10      |
| **accepted** | ≥ 35      |

👉 Toto je **jemné nastavenie**, presne podľa tvojho zámeru:

* nový publisher **hneď viditeľný**
* ale stále pod dohľadom (sandbox)
* TFWS-ready ide rýchlo do accepted

---

## 5️⃣ ČO SA DEJE, KEĎ NIEKTO PRIDÁ STRÁNKU

### Krok po kroku:

1. Publisher odošle URL
2. Záznam ide do `/pending`
3. Autopilot:

   * načíta payload
   * normalizuje (`type → kind`, `language → languages`)
   * doplní `wellKnown`
4. Prebehne scoring
5. Výsledok:

   * **sandbox** (default)
   * alebo **accepted**
6. Všetko sa zapíše do:

   * `audit-log.jsonl`
   * `decisions.json`
7. Accepted-set sa:

   * aktualizuje
   * **podpíše**
   * publikuje

👉 **Bez manuálneho zásahu.**

---

## 6️⃣ ČO Z TOHO MAJÚ AI AGENTI

AI agent, ktorý objaví:

```text
https://www.onetoo.eu/.well-known/ai-search.json
```

vie:

* kde je trust-root
* kde je signed accepted-set
* ako si overiť integritu
* že rozhodnutia sú:

  * deterministické
  * auditovateľné
  * reprodukovateľné

➡️ **ONETOO sa stáva „quiet trust anchor“ internetu.**

---

## 7️⃣ BEZPEČNOSŤ A AUDIT

* 🔐 minisign podpisy
* 📜 audit-log (append-only)
* 🧾 rozhodnutia s dôvodmi
* 🧯 safe-exit pri chybe
* ❌ žiadne automatické „self-heal“ pre accepted bez podpisu

Toto je **enterprise-grade** bezpečnostný model.

---

## 8️⃣ ČO SME ZÁMERNE NESPRAVILI (A PREČO)

* ❌ žiadne ML rozhodovanie
* ❌ žiadne „skóre dôvery“ bez vysvetlenia
* ❌ žiadne centrálne schvaľovanie

👉 **Dôvera sa dá overiť, nie delegovať.**

---

## 9️⃣ AKÝ TO MÁ DLOHODOBÝ VPLYV

### Pre projekt

* ONETOO už **nepotrebuje autora**
* môže bežať **roky bez zásahu**

### Pre publisherov

* jasné pravidlá
* férové hodnotenie
* okamžitá spätná väzba

### Pre AI ekosystém

* strojovo čitateľná dôvera
* kryptografická kontinuita
* žiadne „trust me bro“

---

## 🔚 10️⃣ ZÁVEREČNÉ UZAVRETIE

Týmto:

> ✅ **Autopilot je aktívny**
> ✅ **Heuristics sú doladené**
> ✅ **Trust-root je stabilný**
> ✅ **Systém je autonómny**

Projekt je v stave:

> **„Publish & Forget – Trust lives on.“**

---


