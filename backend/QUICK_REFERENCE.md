# Quick Reference: Switching AI Providers

## Current Providers

| Provider | Type | Cost | Use Case |
|----------|------|------|----------|
| **Gemini** | Cloud (Google) | Paid | Best quality, fast |
| **Ollama** | Local | Free | Privacy, offline |
| **CloudQwen** | Cloud (Alibaba) | Paid | Multimodal, cost-effective |

## Switch Provider

Edit `.env` and change **ONE line**:

```env
# Use Gemini (Google AI)
AI_PROVIDER=gemini

# Use Ollama (Local)
AI_PROVIDER=ollama

# Use CloudQwen (Alibaba)
AI_PROVIDER=cloudqwen
```

Then restart the backend.

## CloudQwen Setup

1. Get API key from: https://dashscope.aliyuncs.com/
2. Add to `.env`:
```env
AI_PROVIDER=cloudqwen
CLOUDQWEN_API_KEY=sk-your-key-here
```
3. Restart backend

## Add New Provider

Only need to edit **3 files**:

1. Create `app/services/YOUR_provider_service.py`
2. Edit `app/services/model_factory.py` - add 1 line
3. Edit `app/config.py` - add config section

See [AI_PROVIDERS.md](file:///d:/AF/Projects/google-deepmind-hackathon/justitia-lens/backend/AI_PROVIDERS.md) for details.

## Test

Run in backend directory:
```bash
python test_providers.py
```

## Troubleshooting

**Error: "Unknown AI provider"**
- Check `AI_PROVIDER` spelling in `.env`
- Must be: `gemini`, `ollama`, or `cloudqwen`

**API Key Error**
- Check key is correct
- For CloudQwen: starts with `sk-`
- For Gemini: get from Google AI Studio

**Connection Error**
- Gemini/CloudQwen: Check internet
- Ollama: Ensure running locally (`ollama serve`)
