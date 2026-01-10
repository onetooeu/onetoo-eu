# Autopilot scoring – prehľad

Scoring je heuristický, ale **konzistentný a auditovateľný**.

## Skóre (0–100)
Body podľa signálov:
- `.well-known/` existuje a odpovedá 200
- `.well-known/minisign.pub` existuje (200)
- `.well-known/sha256.json` existuje (200)
- `security.txt` existuje (200)
- repo link na GitHub
- allowlist bonus (host/repo)

Thresholdy v `autopilot/heuristics.json`:
- `min_score_to_accept` (default 70)
- `min_score_to_sandbox` (default 40)

## Rozhodnutie
- accept: score ≥ accept threshold
- sandbox: medzi sandbox a accept
- reject: hard_fail alebo score < sandbox threshold
