# Security Policy

## Deployment Security

This repository is designed for **safe public deployment**. No sensitive credentials are included.

### ✅ What's Safe to Deploy

| Data Type | Example | Status |
|-----------|---------|--------|
| **Public Wallet Address** | `0x0c0feb248548e33571584809113891818d4b0805` | ✅ Safe - Designed to be public (like email for receiving payments) |
| **Payment Network** | "base-mainnet" | ✅ Safe - Public blockchain network |
| **AI Model Names** | "gemini-2.5-flash" | ✅ Safe - Public model identifier (no authentication) |
| **System Prompts** | Babeta's personality | ✅ Safe - Public configuration |
| **Service Prices** | 3-50 USDC | ✅ Safe - Public pricing |

### 🔒 What's NOT in This Repo

| Sensitive Data | Why It's Not Here | Where It Actually Is |
|----------------|-------------------|---------------------|
| **Private Keys** | Can spend funds | ❌ Only in local payment-skill wallet |
| **Gemini API Key** | AI service access | ❌ Only in local credentials.json |
| **Claude API Key** | AI service access | ❌ Only in local credentials.json |
| **OpenAI API Key** | AI service access | ❌ Only in local credentials.json |
| **Moltbook API Key** | Social platform access | ❌ Only in local credentials.json |

## Why This Design is Secure

### 1. Provider Role = Receiving Only

**This service is a PROVIDER (receives payments):**
- ✅ Gives out public wallet address to clients
- ✅ Verifies payment signatures (no private key needed)
- ✅ Checks blockchain for payments (public data)
- ❌ Never signs transactions
- ❌ Never spends money
- ❌ Doesn't need private keys

**Like a merchant:**
- Merchant shares their account number (public)
- Customer sends money to that account
- Merchant verifies payment was received
- Merchant delivers product

### 2. No AI API Calls Needed

**Service fulfillment uses templates:**
```python
# ivxp-fulfillment.py
def fulfill_service(order_id, service_type, description):
    # Uses pre-written templates, not AI APIs
    return {'content': template_content}
```

**No API calls = No API keys needed**

### 3. Signature Verification (Not Creation)

**Provider verifies signatures without private keys:**
```python
# Cryptographic verification (safe operation)
def verify_signature(message, signature, expected_address):
    recovered_address = recover_from_signature(message, signature)
    return recovered_address == expected_address
```

**This is mathematically safe** - recovering address from signature doesn't expose private key.

## Files in This Repository

### Safe Files (Public Information)

```
✅ babeta-ivxp-service.py     Main service entry point
✅ ivxp-provider.py            IVXP protocol implementation
✅ ivxp-fulfillment.py         Service templates
✅ babeta-config.json          Public configuration
✅ requirements.txt            Python dependencies
✅ Procfile                    Railway start command
✅ railway.json                Railway configuration
✅ .gitignore                  Protects sensitive files
```

### Files NOT in Repository

```
❌ credentials.json            Has API keys (local only)
❌ babeta-agent.py             Uses API keys (not needed for IVXP)
❌ babeta-payments.py          Uses payment-skill (not needed)
❌ ivxp-client.py              Uses private keys (client-side only)
❌ test-*.py                   Local testing files
❌ *.key, *.pem                Any key files
❌ wallet-keystore             Payment wallet (local only)
```

## Verification

### Before Each Deployment

The repository has been verified to NOT contain:
- ❌ Private keys (checked with `grep "BEGIN.*PRIVATE"`)
- ❌ API keys (checked with `grep "sk-ant-\|AIza\|sk-proj-"`)
- ❌ Credentials files
- ❌ Wallet keystores

### You Can Verify Too

```bash
# Clone repo
git clone https://github.com/franksprotocols/babeta-ivxp-service.git
cd babeta-ivxp-service

# Check for private keys
grep -r "BEGIN.*PRIVATE" . && echo "FOUND PRIVATE KEY!" || echo "✅ No private keys"

# Check for API keys
grep -r "sk-ant-\|AIza\|sk-proj-" . && echo "FOUND API KEY!" || echo "✅ No API keys"

# List all files
git ls-files
```

## Deployment Environments

### Railway (Production)
- ✅ HTTPS by default
- ✅ Environment isolation
- ✅ Can see: Public code, public wallet address
- ❌ Cannot see: Local credentials, private keys

### What Railway Receives
```
Public wallet address:  0x0c0feb248548e33571584809113891818d4b0805
AI model name:          gemini-2.5-flash
Service code:           Flask app for IVXP protocol
Configuration:          babeta-config.json (public only)
```

### What Railway Does NOT Receive
```
Private keys:      NOT in deployment
API keys:          NOT in deployment
Credentials:       NOT in deployment
```

## Protected by .gitignore

The following patterns are protected from accidental commits:

```gitignore
# Sensitive files
.env
*.key
*.pem
*_private_key*
credentials.json
secrets.json
wallet-keystore

# Files that use sensitive data
babeta-agent.py          # Uses API keys
babeta-payments.py       # Uses payment-skill
ivxp-client.py           # Uses private keys
test-*.py                # May contain test credentials
```

## Reporting Security Issues

If you find a security vulnerability:

1. **DO NOT** open a public issue
2. Email: (contact info)
3. Include:
   - Description of the issue
   - Steps to reproduce
   - Potential impact

## Security Best Practices

### For Deployment
- ✅ Use HTTPS (Railway provides by default)
- ✅ Review code before deploying
- ✅ Monitor logs for suspicious activity
- ✅ Keep dependencies updated

### For Development
- ❌ Never commit credentials
- ❌ Never commit private keys
- ❌ Never commit API keys
- ✅ Use .env for local secrets (gitignored)
- ✅ Use environment variables for sensitive data

## Questions?

See also:
- **IVXP Protocol**: https://github.com/franksprotocols/ivxp-protocol
- **Railway Security**: https://docs.railway.app/reference/security

---

**Last Updated**: 2026-02-05
**Verified By**: Security audit (automated + manual review)
