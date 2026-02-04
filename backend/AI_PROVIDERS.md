# AI Provider System - Configuration Guide

This document explains how to configure and add AI providers to the Justitia Lens backend.

## Available Providers

### 1. **Gemini** (Google AI)
- **Text Model**: gemini-2.0-flash
- **Vision Model**: gemini-2.0-flash (multimodal)
- **API Key Required**: Yes

### 2. **Ollama** (Local/Self-hosted)
- **Text Model**: llama3.1:8b (configurable)
- **Vision Model**: llava (configurable)
- **API Key Required**: No

### 3. **CloudQwen** (Alibaba Cloud)
- **Text Model**: qwen-plus (configurable)
- **Vision Model**: qwen-vl-plus (configurable)
- **API Key Required**: Yes

## Configuration

### Setting Up a Provider

1. **Edit your `.env` file** and set the `AI_PROVIDER` variable:

```env
AI_PROVIDER=gemini  # Options: gemini, ollama, cloudqwen
```

2. **Configure provider-specific settings:**

#### For Gemini:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

#### For Ollama:
```env
OLLAMA_BASE_URL=http://localhost:11434/api
OLLAMA_MODEL=llama3.1:8b
OLLAMA_VISION_MODEL=llava
```

#### For CloudQwen:
```env
CLOUDQWEN_API_KEY=your_cloudqwen_api_key_here
CLOUDQWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
CLOUDQWEN_MODEL=qwen-plus
CLOUDQWEN_VISION_MODEL=qwen-vl-plus
```

## Adding a New Provider

The system is designed to make adding new AI providers easy. Follow these steps:

### Step 1: Create a New Service Class

Create a new file in `app/services/` (e.g., `new_provider_service.py`):

```python
from typing import Optional
from app.config import settings
from app.services.base_provider import BaseAIProvider
import aiohttp
import json

class NewProviderService(BaseAIProvider):
    def __init__(self):
        self.api_key = settings.NEW_PROVIDER_API_KEY
        self.base_url = settings.NEW_PROVIDER_BASE_URL
        self.model = settings.NEW_PROVIDER_MODEL
        self.vision_model = settings.NEW_PROVIDER_VISION_MODEL
    
    async def generate_json(self, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Implement JSON generation for your provider.
        Must return a dict with parsed JSON response.
        On error, return {"error": "error message"}
        """
        # Your implementation here
        pass
    
    async def analyze_image(self, image_path: str, prompt: str, model_name: Optional[str] = None) -> dict:
        """
        Implement image analysis for your provider.
        Must read the image file, send to API, and return parsed JSON.
        On error, return {"error": "error message"}
        """
        # Your implementation here
        pass
    
    async def generate_content(self, prompt: str, model_name: Optional[str] = None) -> str:
        """
        Optional: Implement plain text generation.
        If not implemented, base class will use generate_json.
        """
        # Your implementation here (optional)
        pass
```

### Step 2: Add Configuration Settings

Edit `app/config.py` and add your provider's settings:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # New Provider
    NEW_PROVIDER_API_KEY: str = "placeholder_key"
    NEW_PROVIDER_BASE_URL: str = "https://api.newprovider.com/v1"
    NEW_PROVIDER_MODEL: str = "default-model"
    NEW_PROVIDER_VISION_MODEL: str = "default-vision-model"
```

Update the `AI_PROVIDER` comment:
```python
AI_PROVIDER: str = "ollama" # Options: "gemini", "ollama", "cloudqwen", "newprovider"
```

### Step 3: Register the Provider

Edit `app/services/model_factory.py` and add your provider to the `_initialize_providers()` function:

```python
def _initialize_providers():
    """Initialize the provider registry with all available providers."""
    from app.services.gemini_service import GeminiService
    from app.services.ollama_service import OllamaService
    from app.services.cloudqwen_service import CloudQwenService
    from app.services.new_provider_service import NewProviderService  # Add this
    
    register_provider("gemini", GeminiService)
    register_provider("ollama", OllamaService)
    register_provider("cloudqwen", CloudQwenService)
    register_provider("newprovider", NewProviderService)  # Add this
```

### Step 4: Update Environment Example

Edit `.env.example` to document the new provider:

```env
# New Provider Configuration (if using newprovider)
NEW_PROVIDER_API_KEY=your_key_here
NEW_PROVIDER_BASE_URL=https://api.newprovider.com/v1
NEW_PROVIDER_MODEL=default-model
NEW_PROVIDER_VISION_MODEL=default-vision-model
```

### Step 5: Use the Provider

Set `AI_PROVIDER=newprovider` in your `.env` file and restart the application.

**That's it!** All agents will automatically use your new provider without any code changes.

## Architecture Overview

```
┌─────────────────────────────────────┐
│      Agents (Narrative, Vision,    │
│         Synthesizer)                │
└──────────────┬──────────────────────┘
               │ Uses
               ▼
     ┌─────────────────┐
     │  Model Factory  │
     │  get_provider() │
     └────────┬────────┘
              │ Returns
              ▼
   ┌──────────────────────┐
   │  BaseAIProvider      │
   │  (Abstract Interface)│
   └──────────┬───────────┘
              │ Implements
    ┌─────────┴──────────────────┐
    │                            │
    ▼                            ▼
┌─────────┐  ┌──────────┐  ┌────────────┐
│ Gemini  │  │  Ollama  │  │ CloudQwen  │
│ Service │  │ Service  │  │  Service   │
└─────────┘  └──────────┘  └────────────┘
```

## Key Benefits

1. **Zero Agent Changes**: Agents automatically use whichever provider is configured
2. **Single Point of Configuration**: Change `AI_PROVIDER` in one place
3. **Type Safety**: All providers implement the same interface
4. **Error Handling**: Standardized error response format across providers
5. **Easy Testing**: Mock the factory to test with different providers

## Troubleshooting

### "Unknown AI provider" Error

Check that:
1. `AI_PROVIDER` in `.env` matches a registered provider name (case-insensitive)
2. The provider is registered in `model_factory.py`

### API Connection Errors

For Gemini/CloudQwen:
- Verify your API key is correct
- Check internet connectivity
- Ensure API endpoint URL is correct

For Ollama:
- Verify Ollama is running locally
- Check the base URL and port
- Ensure the model is downloaded (`ollama pull llama3.1:8b`)

### JSON Parsing Errors

All providers should return valid JSON. If you see parsing errors:
- Check the provider's API response format
- Ensure prompts request JSON output
- Review the provider's `generate_json()` implementation

## Example Usage

```python
from app.services.model_factory import get_provider

# Get the configured provider
llm = get_provider()

# Use it for text generation
result = await llm.generate_json("Analyze this text...")

# Use it for vision
result = await llm.analyze_image("/path/to/image.jpg", "Describe this image...")

# Get a specific provider (overrides config)
gemini = get_provider("gemini")
ollama = get_provider("ollama")
cloudqwen = get_provider("cloudqwen")
```
