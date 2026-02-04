from typing import Optional
from app.config import settings
from app.services.base_provider import BaseAIProvider


# Provider registry - maps provider names to their service classes
_PROVIDER_REGISTRY = {}


def register_provider(name: str, provider_class):
    """
    Register a new AI provider in the factory.
    
    Args:
        name: Provider identifier (e.g., 'gemini', 'ollama', 'cloudqwen')
        provider_class: The service class implementing BaseAIProvider
    """
    _PROVIDER_REGISTRY[name.lower()] = provider_class


def get_provider(provider_name: Optional[str] = None) -> BaseAIProvider:
    """
    Factory function to get an AI provider instance.
    
    Args:
        provider_name: Name of the provider to instantiate.
                      If None, uses settings.AI_PROVIDER
    
    Returns:
        BaseAIProvider: Instantiated provider service
        
    Raises:
        ValueError: If the provider name is not registered
    """
    # Use default provider from settings if not specified
    name = (provider_name or settings.AI_PROVIDER).lower()
    
    # Lazy import to avoid circular dependencies
    if not _PROVIDER_REGISTRY:
        _initialize_providers()
    
    if name not in _PROVIDER_REGISTRY:
        available = ", ".join(_PROVIDER_REGISTRY.keys())
        raise ValueError(
            f"Unknown AI provider: '{name}'. "
            f"Available providers: {available}"
        )
    
    provider_class = _PROVIDER_REGISTRY[name]
    return provider_class()


def _initialize_providers():
    """
    Initialize the provider registry with all available providers.
    This is called lazily on first use to avoid import issues.
    """
    from app.services.gemini_service import GeminiService
    from app.services.ollama_service import OllamaService
    from app.services.cloudqwen_service import CloudQwenService
    
    register_provider("gemini", GeminiService)
    register_provider("ollama", OllamaService)
    register_provider("cloudqwen", CloudQwenService)


def get_available_providers() -> list[str]:
    """
    Get a list of all registered provider names.
    
    Returns:
        list[str]: List of available provider identifiers
    """
    if not _PROVIDER_REGISTRY:
        _initialize_providers()
    
    return list(_PROVIDER_REGISTRY.keys())
