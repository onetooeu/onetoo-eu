# TFWS v2 Incident Playbooks

## 1) KEY MISMATCH (critical)
**Signal:** minisign verify fails with key id mismatch  
**Agent response:** RED + halt trust  
**Operator steps:**
1. Identify which secret key produced the signature (local key vault).
2. Re-sign the exact artifact (key-history, trust-state, sha256, release, targets).
3. Deploy and purge CDN for:
   - `/.well-known/*`
   - `/dumps/*`
4. Publish incident record with:
   - first seen time
   - affected endpoints
   - old hash vs new hash
   - resolution commit id

## 2) ROLLBACK SUSPECT (high)
**Signal:** signatures pass, but epoch/tag regresses  
**Agent response:** ORANGE (degrade)  
**Operator steps:**
1. Verify branch protection and deployment source branch.
2. Check Pages deploy history for accidental older commit.
3. Re-issue fresh signed bundle and bump epoch/tag.
4. Consider monotonic build counter stored in trust-state.

## 3) CACHE POISON / STALE EDGE (medium)
**Signal:** same URL yields different hashes (often per colo)  
**Agent response:** YELLOW  
**Operator steps:**
1. Purge cache for exact artifact paths.
2. Keep TTL short for integrity endpoints (e.g. 300s).
3. Add deploy probe marker:
   - `/.well-known/_deploy_probe.txt` (contains commit id + timestamp)
4. In agent verification always use `?ts=` cache buster.

## 4) MIRROR DIVERGENCE (high)
**Signal:** GitHub raw != Pages != Prod for same artifacts  
**Agent response:** ORANGE  
**Operator steps:**
1. Confirm intended repo + branch for deployment.
2. Confirm prod routing to right Pages project.
3. Force redeploy + purge.
4. Publish incident with authoritative hash.

## 5) INCOMPLETE BUNDLE (medium)
**Signal:** referenced integrity files missing  
**Agent response:** YELLOW  
**Operator steps:**
1. Restore missing files.
2. Rebuild + re-sign if bundle consistency broken.
3. Add CI rule: fail build if any referenced artifact missing.
