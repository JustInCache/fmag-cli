"""
Audio generation providers for FMAG.

Supports multiple AI audio generation backends with a unified interface.
"""

from .base import AudioProvider, ProviderError
from .audiogen_provider import AudioGenProvider
from .bark_provider import BarkProvider

__all__ = [
    "AudioProvider",
    "ProviderError",
    "AudioGenProvider",
    "BarkProvider",
    "get_provider",
    "list_providers",
]


# Registry of available providers
PROVIDERS = {
    "audiogen": AudioGenProvider,
    "bark": BarkProvider,
}


def get_provider(name: str, debug: bool = False) -> AudioProvider:
    """
    Get a provider instance by name.
    
    Args:
        name: Provider name ('audiogen' or 'bark')
        debug: Enable debug logging
    
    Returns:
        Configured provider instance
    
    Raises:
        ValueError: If provider name is unknown
    """
    if name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(
            f"Unknown provider '{name}'. Available: {available}"
        )
    
    return PROVIDERS[name](debug=debug)


def list_providers() -> list[str]:
    """List all available provider names."""
    return list(PROVIDERS.keys())


def auto_detect_provider(debug: bool = False) -> AudioProvider:
    """
    Auto-detect the best available provider based on environment.
    
    Checks for API keys and installed dependencies to determine
    which provider to use.
    
    Args:
        debug: Enable debug logging
    
    Returns:
        The best available provider instance
    """
    import os
    
    # Check for OpenAI API key (AudioGen)
    if os.environ.get("OPENAI_API_KEY"):
        if debug:
            from rich.console import Console
            Console().print("[dim]Auto-detected: AudioGen (OpenAI)[/dim]")
        return AudioGenProvider(debug=debug)
    
    # Check for Bark
    try:
        import bark
        if debug:
            from rich.console import Console
            Console().print("[dim]Auto-detected: Bark[/dim]")
        return BarkProvider(debug=debug)
    except ImportError:
        pass
    
    # Default to AudioGen (will fail gracefully if not configured)
    return AudioGenProvider(debug=debug)

