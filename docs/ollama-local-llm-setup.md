# Ollama local LLM setup (CV extraction)

## What this is

The LLM fallback path in `POST /ai/upload/` can now use a local
Ollama server instead of (or before) the Groq cloud API. This makes
the LLM path:

- **Free** — no per-call API cost.
- **Private** — the CV never leaves your server (good for seafarer PII).
- **Reliable** — no rate limits, no leaked API key risk.

The cloud LLM providers (Groq, Gemini) are kept as the ultimate
fallback in case Ollama is down.

## Provider priority

The LLM router in `ai_document/document_to_json.py` tries providers
in this order:

1. **Ollama (local, free)** — when `OLLAMA_HOST` is set and Ollama
   is reachable.
2. **Groq (cloud)** — when a Groq key is in the request or env.
3. **Gemini (cloud, last resort)** — when a Gemini key is in the
   request or env.

If **all three** fail, the request returns 400 with an
`invalid_document` error and a message explaining how to fix it.

## Server install (one-time, ~5-10 min)

Run these on the prod server (`srv1080138`):

```bash
# 1. Install Ollama (Linux x86_64 installer).
curl -fsSL https://ollama.com/install.sh | sh

# 2. Pull the recommended model. 4.7 GB download.
#    Good default: qwen2.5:7b (multilingual, JSON-mode, Arabic support)
ollama pull qwen2.5:7b

# 3. Verify Ollama is running and the model is loaded.
ollama list
# Expected: qwen2.5:7b  ...  4.7 GB

# 4. Quick smoke test (should respond in JSON).
curl http://127.0.0.1:11434/api/generate -d '{
  "model": "qwen2.5:7b",
  "prompt": "Return JSON: {\"name\": string} for: Ahmed Mohamed",
  "format": "json",
  "stream": false
}'
```

`ollama serve` is the default systemd service — it listens on
`127.0.0.1:11434`. You can check with:

```bash
systemctl status ollama
curl -s http://127.0.0.1:11434/api/tags
```

## App configuration

Set the env var on the Django app so the LLM router knows where
Ollama lives:

```bash
# In the gunicorn systemd unit or wherever you start the app:
export OLLAMA_HOST="http://127.0.0.1:11434"
# Optional overrides:
export OLLAMA_MODEL="qwen2.5:7b"        # default
export OLLAMA_ENABLED="true"            # default; set to "false" to skip Ollama
export OLLAMA_TIMEOUT_SECONDS="60"      # default
```

Then restart gunicorn. The new env var takes effect on the next
request.

## How /ai/upload/ behaves now

Once `OLLAMA_HOST` is set:

- **Sakr-form CV** → `extractor: "sakr_template"` (no LLM at all).
- **Generic CV** → `extractor: "groq_llm"`, powered by Ollama
  locally. **No API key needed in the request.**
- **Ollama down** → falls through to Groq (if you have a key) or
  Gemini (if you have a key). Existing behaviour preserved.

The response shape is unchanged — still matches `POST /ai/parse/`.

## Verifying it's working

```bash
# From your dev machine, with admin JWT token in $TOKEN:
curl -X POST http://srv1080138:8000/ai/upload/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_cv.pdf"
# Look for: "extractor": "groq_llm" + CV data + saved=true
# Check gunicorn logs: should see no Groq/Gemini calls.

# Verify Ollama served the request:
journalctl -u ollama --since "1 minute ago" | grep -i "POST /api/chat"
```

## Disabling Ollama without uninstalling

If you ever need to bypass Ollama (e.g. testing the cloud path
without stopping the Ollama service):

```bash
# Option 1: env var
export OLLAMA_ENABLED="false"
systemctl restart gunicorn

# Option 2: per-request override (in api_keys_config JSON)
# {"ollama_disabled": true}
```

The router will skip Ollama and go straight to Groq/Gemini.

## Recommended models

| Model | Size | When to use it |
|---|---|---|
| **`qwen2.5:7b`** ⭐ | 4.7 GB | Default. Best JSON-mode + multilingual (Arabic-friendly) |
| `qwen2.5:14b` | 9 GB | Better on messy/unusual CVs, needs 16 GB RAM |
| `llama3.1:8b` | 4.7 GB | Solid general-purpose English-only |
| `mistral-nemo:12b` | 7 GB | Excellent at structured JSON output, 128k context |
| `phi3.5:3.8b` | 2.3 GB | Tiny, fast, English-only, lower accuracy |

To switch models:

```bash
ollama pull qwen2.5:14b
export OLLAMA_MODEL="qwen2.5:14b"
systemctl restart gunicorn
```

The router hot-swaps — no app code change needed.

## Troubleshooting

**`Ollama init failed` in gunicorn logs**
→ Ollama not running. `systemctl status ollama` and start it.

**Slow first request (10-30 sec)**
→ Ollama loads the model into RAM on first use. Subsequent
requests are fast. This is normal; you can preload with
`ollama run qwen2.5:7b ""` after install.

**Ollama OOM-killed**
→ Model too big for the VPS. Drop to a smaller model
(`qwen2.5:7b` → `phi3.5:3.8b`) or add swap.

**`validation_error: No LLM provider is available`**
→ Ollama not running AND no Groq/Gemini key in the request.
Either start Ollama or supply a cloud key.

**`format=json` not respected by older models**
→ qwen2.5+ / llama3.1+ / mistral-nemo all support JSON-mode.
If using an older model, upgrade.
