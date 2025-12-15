"""
Core ambience generation logic.

Orchestrates the generation pipeline: preset loading, provider
selection, audio generation, and post-processing.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

from .presets import get_preset, MoodPreset, PRESETS
from .audio_utils import AudioProcessor
from .providers import get_provider, auto_detect_provider, AudioProvider
from .providers.base import GenerationResult, ProviderError

console = Console()


class GenerationConfig:
    """Configuration for ambience generation."""
    
    def __init__(
        self,
        mood: str,
        duration_minutes: float = 2.0,
        provider: Optional[str] = None,
        output_dir: str = "./output",
        debug: bool = False,
        normalize: bool = True,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
        loop_optimize: bool = True,
        crossfade: float = 1.0,
    ):
        """
        Initialize generation configuration.
        
        Args:
            mood: Mood preset name or custom prompt
            duration_minutes: Duration in minutes (1-5)
            provider: Provider name or None for auto-detect
            output_dir: Output directory for generated files
            debug: Enable debug logging
            normalize: Normalize audio volume
            fade_in: Fade-in duration in seconds
            fade_out: Fade-out duration in seconds
            loop_optimize: Enable loop optimization
            crossfade: Crossfade duration for loop optimization
        """
        self.mood = mood
        self.duration_minutes = max(1.0, min(5.0, duration_minutes))
        self.provider = provider
        self.output_dir = output_dir
        self.debug = debug
        self.normalize = normalize
        self.fade_in = fade_in
        self.fade_out = fade_out
        self.loop_optimize = loop_optimize
        self.crossfade = crossfade
    
    @property
    def duration_seconds(self) -> float:
        """Get duration in seconds."""
        return self.duration_minutes * 60


class AmbienceGenerator:
    """
    Main ambience generation orchestrator.
    
    Handles the complete pipeline from mood selection to
    final processed audio output.
    """
    
    def __init__(self, config: GenerationConfig):
        """
        Initialize the ambience generator.
        
        Args:
            config: Generation configuration
        """
        self.config = config
        self.console = Console()
        
        # Initialize provider
        if config.provider:
            self._provider = get_provider(config.provider, debug=config.debug)
        else:
            self._provider = auto_detect_provider(debug=config.debug)
        
        # Initialize audio processor
        self._processor = AudioProcessor(debug=config.debug)
    
    @property
    def provider(self) -> AudioProvider:
        """Get the current audio provider."""
        return self._provider
    
    def generate(self) -> str:
        """
        Generate ambient audio based on configuration.
        
        Returns:
            Path to the generated MP3 file
        
        Raises:
            ValueError: If mood preset is invalid
            ProviderError: If generation fails
        """
        # Get preset or use custom prompt
        preset = get_preset(self.config.mood)
        if preset:
            prompt = preset.to_prompt()
            mood_name = preset.name
            mood_emoji = preset.emoji
        else:
            # Treat as custom prompt
            prompt = self.config.mood
            mood_name = "custom"
            mood_emoji = "🎵"
        
        # Generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"fmag-{mood_name}-{timestamp}.mp3"
        output_path = os.path.join(self.config.output_dir, output_filename)
        
        # Ensure output directory exists
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            # Step 1: Generate raw audio
            task = progress.add_task(
                f"[cyan]{mood_emoji} Generating audio with {self._provider.name}...",
                total=100
            )
            
            result = self._provider.generate_audio(
                prompt=prompt,
                duration_seconds=self.config.duration_seconds,
                output_path=output_path
            )
            progress.update(task, completed=50)
            
            # Step 2: Process audio
            progress.update(task, description="[cyan]🎛️  Processing audio...")
            
            processed_path = self._processor.process_full_pipeline(
                input_path=result.audio_path,
                output_path=output_path,
                normalize=self.config.normalize,
                fade_in=self.config.fade_in,
                fade_out=self.config.fade_out,
                loop_optimize=self.config.loop_optimize,
                crossfade=self.config.crossfade
            )
            progress.update(task, completed=100)
        
        # Clean up intermediate WAV file if it exists
        wav_path = output_path.replace('.mp3', '.wav')
        if os.path.exists(wav_path) and wav_path != processed_path:
            try:
                os.remove(wav_path)
            except OSError:
                pass
        
        return processed_path
    
    def validate(self) -> list[str]:
        """
        Validate the configuration before generation.
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Check mood
        preset = get_preset(self.config.mood)
        if not preset and len(self.config.mood) < 10:
            errors.append(
                f"Unknown mood '{self.config.mood}'. "
                f"Use a preset or provide a detailed custom prompt."
            )
        
        # Check duration
        if self.config.duration_minutes < 1:
            errors.append("Duration must be at least 1 minute.")
        elif self.config.duration_minutes > 5:
            errors.append("Duration cannot exceed 5 minutes.")
        
        # Check provider
        if not self._provider.is_available():
            errors.append(
                f"Provider '{self._provider.name}' is not available.\n"
                f"{self._provider.get_config_help()}"
            )
        
        return errors


def quick_generate(
    mood: str,
    duration_minutes: float = 2.0,
    provider: Optional[str] = None,
    output_dir: str = "./output",
    debug: bool = False
) -> str:
    """
    Quick helper function for simple generation.
    
    Args:
        mood: Mood preset name
        duration_minutes: Duration in minutes
        provider: Provider name (optional)
        output_dir: Output directory
        debug: Enable debug mode
    
    Returns:
        Path to generated MP3 file
    """
    config = GenerationConfig(
        mood=mood,
        duration_minutes=duration_minutes,
        provider=provider,
        output_dir=output_dir,
        debug=debug
    )
    
    generator = AmbienceGenerator(config)
    return generator.generate()


def list_available_moods() -> list[tuple[str, str, str]]:
    """
    List all available moods with their descriptions.
    
    Returns:
        List of (name, emoji, description) tuples
    """
    return [
        (name, preset.emoji, preset.description)
        for name, preset in PRESETS.items()
    ]

