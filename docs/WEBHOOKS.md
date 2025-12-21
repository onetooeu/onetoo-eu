# WEBHOOKS (Planned)

This project supports two notification modes:

## 1) Pull (available now)
- Atom feeds:
  - /changelog/feed.xml
  - /incidents/feed.xml
- JSON indexes:
  - /changelog/index.json
  - /incidents/index.json

## 2) Webhook push (planned)
Webhook push is a planned capability. This repository publishes a declarative contract:
- /.well-known/webhooks.json

### Event types

cat > docs/WEBHOOKS.md <<'MD'
# WEBHOOKS (Planned)

This project supports two notification modes:

## 1) Pull (available now)
- Atom feeds:
  - /changelog/feed.xml
  - /incidents/feed.xml
- JSON indexes:
  - /changelog/index.json
  - /incidents/index.json

## 2) Webhook push (planned)
Webhook push is a planned capability. This repository publishes a declarative contract:
- /.well-known/webhooks.json

### Event types
- changelog.new_entry
- incidents.updated

### Security recommendations
Webhook deliveries SHOULD use:
- mTLS where possible
- HMAC-SHA256 signatures (timestamp + nonce)
- replay protection

### Status
Planned. For now, integrators should use Pull mode (Atom/JSON) for reliable consumption.
