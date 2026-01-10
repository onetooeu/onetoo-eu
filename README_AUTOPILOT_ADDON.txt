Tento ZIP je "addon" balík.

Použitie:
1) Rozbaľ obsah ZIP do koreňa repozitára onetoo-eu (pridá/ prepíše súbory).
2) Skontroluj: git diff
3) Commit + push

Poznámka:
Ak už máš vlastnú verziu workflow/scriptu, prenes len tieto zmeny:
- endpoint pending je /contrib/v2/pending (nie index.json)
- autopilot vytvára accept/sandbox/reject + audit log
