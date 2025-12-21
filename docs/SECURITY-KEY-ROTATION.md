# Security & Key Rotation (Playbook)
This playbook is designed for long-term operations.

## Contacts
- security@onetoo.eu
- trust@onetoo.eu

## Rotation triggers
- Scheduled rotation (recommended)
- Any suspected compromise
- Major platform changes

## Steps
1. Create new keypair
2. Publish new public key (`/.well-known/pgp-key.txt` or your chosen key distribution)
3. Update documentation and pointers
4. Dual-sign for a defined transition window
5. Remove old signing key from production
6. Record change in `/api/v1/meta/changelog.json`
