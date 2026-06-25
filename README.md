# 9router + BTL Setup Guide

## Overview
9router — Advanced AI router with combos, fallback, quota tracking.
BTL (Bad Theory Labs) — Free AI API provider with 200+ keys.

## API Info
- **Base URL:** `https://api.badtheorylabs.com/v1`
- **Model:** `deepseek-v4-pro`
- **Auth:** Supabase access token (NOT the `gw_` keys directly)

## Setup

### 1. Install 9router
```bash
npm install -g 9router
9router  # starts on http://localhost:20128
```

### 2. Prepare API keys
```bash
# Create key file (one key per line, starts with gw_)
cat > ~/.hermes/btl-keys-active.txt << 'EOF'
gw_your_key_1_here
gw_your_key_2_here
gw_your_key_3_here
EOF
```

### 3. Add keys to 9router (bulk via SQLite)
```bash
python3 setup_9router.py
```

### 4. Restart 9router
```bash
pkill -9 -f 9router; sleep 2
cd ~/.9router && { nohup 9router --log --skip-update > /tmp/9r.log 2>&1 & }
sleep 6
curl -s http://localhost:20128/api/health
```

### 5. Test
```bash
curl -s http://localhost:20128/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"btl-deepseek","messages":[{"role":"user","content":"say ok"}],"max_tokens":5}'
```

## Files
- `setup_9router.py` — Bulk insert script
- `btl-keys-active.txt` — API keys (gw_ format)
- `btl_accounts.txt` — Email|password|workspace
- `btl_apikeys.txt` — Email|apikey|workspace

## Important Notes
- **Auth:** BTL requires Supabase access tokens, not raw `gw_` keys
- **Workspace:** Accounts must have workspace setup completed
- **Domain:** Disposable email domains are blocked by BTL gateway
