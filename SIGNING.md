# Minisign signing (last seal)

This repo is designed so that **release.json** is the signed anchor.

## Files
- Public key: `control/keys/maintainers.pub`
- Anchor: `dumps/release.json`
- Signature output (fixed path): `dumps/sigs/release.json.minisig`

## Sign on Windows (PowerShell)
Assuming you have minisign in `C:\Tools\minisign` and your secret key `ocp-maintainer.key`.

```powershell
cd C:\Tools\minisign
.\minisign.exe -S -s ocp-maintainer.key -m <PATH_TO_REPO>\dumps\release.json -x <PATH_TO_REPO>\dumps\sigs\release.json.minisig
.\minisign.exe -V -p <PATH_TO_REPO>\control\keys\maintainers.pub -m <PATH_TO_REPO>\dumps\release.json -x <PATH_TO_REPO>\dumps\sigs\release.json.minisig
```

## Publish
Commit the updated `dumps/sigs/release.json.minisig` and `control/keys/maintainers.pub`.


## EU Trust Manifest PDF

The official PDF is located at `docs/manifest/EU-Trust-Manifest-v1.0.pdf`.

To verify integrity, use `dumps/sha256.json` (SHA-256) and the minisign public key at `control/keys/maintainers.pub`.

> Note: If a new release updates files but the corresponding minisign signatures are not yet published, treat the SHA-256 list as the integrity reference until signatures are available.


Project operated by **ONETOO.dynamics**.


## Offline signing (Windows)

This repo ships an offline signer for Windows:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sign-all.ps1 -KeyPath "C:\Path\to\onetoo.key" 
```

Optional: sign each pinned target too:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\sign-all.ps1 -KeyPath "C:\Path\to\onetoo.key" -SignTargets
```

It generates and signs:
- `dumps/sha256.json` -> `dumps/sigs/sha256.json.minisig`
- `dumps/targets.json` -> `dumps/sigs/targets.json.minisig`

### Key generation (Minisign)

Generate a new keypair locally (keep the secret key offline):

```bash
minisign -G -p .well-known/minisign.pub -s onetoo.key
```

Publish `.well-known/minisign.pub` and use the secret key to sign artifacts.
