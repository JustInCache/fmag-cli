"""
Base provider interface for audio generation backends.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


class ProviderError(Exception):
    """Exception raised when a provider encounters an error."""
    pass


@dataclass
class GenerationResult:
    """Result of an audio generation request."""
    
    audio_path: str
    duration_seconds: float
    provider_name: str
    prompt_used: str
    metadata: dict
    
    @property
    def duration_minutes(self) -> float:
        """Get duration in minutes."""
        return self.duration_seconds / 60


class AudioProvider(ABC):
    """
    Abstract base class for audio generation providers.
    
    Implement this interface to add support for new AI audio
    generation backends.
    """
    
    name: str = "base"
    description: str = "Base audio provider"
    
    def __init__(self, debug: bool = False):
        """
        Initialize the provider.
        
        Args:
            debug: Enable debug logging
        """
        self.debug = debug
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if this provider is available and configured.
        
        Returns:
            True if the provider can be used
        """
        pass
    
    @abstractmethod
    def generate_audio(
        self,
        prompt: str,
        duration_seconds: float,
        output_path: str,
        **kwargs
    ) -> GenerationResult:
        """
        Generate audio from a text prompt.
        
        Args:
            prompt: Text description of the desired audio
            duration_seconds: Target duration in seconds
            output_path: Path to save the generated audio
            **kwargs: Provider-specific options
        
        Returns:
            GenerationResult with the generated audio details
        
        Raises:
            ProviderError: If generation fails
        """
        pass
    
    def get_config_help(self) -> str:
        """
        Get help text for configuring this provider.
        
        Returns:
            Human-readable configuration instructions
        """
        return f"No special configuration needed for {self.name}"
    
    def log(self, message: str) -> None:
        """Log a debug message if debug mode is enabled."""
        if self.debug:
            from rich.console import Console
            Console().print(f"[dim][{self.name}] {message}[/dim]")

