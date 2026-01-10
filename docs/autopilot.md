# ONETOO Autopilot

Tento balík pridáva do repozitára **autopilot pravidlá (heuristiky)**, **audit log**, a jednoduché **AI‑agent scoring**.

## Čo to robí
- Načíta `pending` z ONETOO Search API (chránené `X-ONETOO-MAINTAINER` tokenom)
- Pre každý pending záznam:
  - stiahne detail (`pending/get?id=...`)
  - vyhodnotí heuristiky + scoring
  - rozhodne: **accept / sandbox / reject**
- Vygeneruje:
  - `dumps/contrib-accepted.json` (stable)
  - `dumps/contrib-sandbox.json` (sandbox)
  - `dumps/contrib-rejected.json` (rejected)
  - `dumps/autopilot/audit-log.jsonl` (append‑only audit log)
  - `dumps/autopilot/decisions.json` (posledné rozhodnutia)

## Secrets (GitHub → repo → Settings → Secrets and variables → Actions)
- `ONETOO_MAINTAINER_TOKEN` – token z curl hlavičky `X-ONETOO-MAINTAINER`
- `ONETOO_SEARCH_BASE` – napr. `https://search.onetoo.eu`

## Workflow
`autopilot-sync-pending.yml` beží na cron alebo manuálne.
