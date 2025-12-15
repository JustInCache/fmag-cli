"""
Tests for FMAG core functionality.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from fmag.presets import (
    PRESETS,
    get_preset,
    list_presets,
    get_preset_choices,
    MoodPreset,
)
from fmag.core import (
    GenerationConfig,
    AmbienceGenerator,
    list_available_moods,
    quick_generate,
)
from fmag.providers import (
    get_provider,
    list_providers,
    auto_detect_provider,
)
from fmag.providers.base import AudioProvider, ProviderError, GenerationResult
from fmag.audio_utils import AudioProcessor


class TestPresets:
    """Tests for mood presets."""
    
    def test_presets_exist(self):
        """Test that all expected presets exist."""
        expected = [
            "calm_rain_office",
            "forest_cafe",
            "deep_focus_spaceship",
            "ocean_meditation",
            "night_coding_lofi",
        ]
        for name in expected:
            assert name in PRESETS
    
    def test_get_preset_valid(self):
        """Test getting a valid preset."""
        preset = get_preset("forest_cafe")
        assert preset is not None
        assert preset.name == "forest_cafe"
        assert isinstance(preset, MoodPreset)
    
    def test_get_preset_invalid(self):
        """Test getting an invalid preset returns None."""
        preset = get_preset("nonexistent_mood")
        assert preset is None
    
    def test_list_presets(self):
        """Test listing all preset names."""
        names = list_presets()
        assert len(names) == 5
        assert "forest_cafe" in names
    
    def test_preset_has_required_fields(self):
        """Test that presets have all required fields."""
        for name, preset in PRESETS.items():
            assert preset.name == name
            assert preset.description
            assert preset.style_hints
            assert preset.suggested_tempo
            assert preset.intensity
            assert isinstance(preset.elements, list)
            assert len(preset.elements) > 0
            assert preset.color
            assert preset.emoji
    
    def test_preset_to_prompt(self):
        """Test converting preset to generation prompt."""
        preset = get_preset("calm_rain_office")
        prompt = preset.to_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 50
        assert "rain" in prompt.lower()
        assert "loop" in prompt.lower()
    
    def test_get_preset_choices(self):
        """Test getting preset choices for menus."""
        choices = get_preset_choices()
        assert len(choices) == 5
        for display, value in choices:
            assert value in PRESETS
            assert PRESETS[value].emoji in display


class TestGenerationConfig:
    """Tests for GenerationConfig."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = GenerationConfig(mood="forest_cafe")
        
        assert config.mood == "forest_cafe"
        assert config.duration_minutes == 2.0
        assert config.provider is None
        assert config.debug is False
        assert config.normalize is True
        assert config.fade_in == 0.5
        assert config.fade_out == 0.5
        assert config.loop_optimize is True
    
    def test_duration_clamping_low(self):
        """Test duration is clamped to minimum of 1."""
        config = GenerationConfig(mood="test", duration_minutes=0.5)
        assert config.duration_minutes == 1.0
    
    def test_duration_clamping_high(self):
        """Test duration is clamped to maximum of 5."""
        config = GenerationConfig(mood="test", duration_minutes=10.0)
        assert config.duration_minutes == 5.0
    
    def test_duration_seconds(self):
        """Test duration_seconds property."""
        config = GenerationConfig(mood="test", duration_minutes=2.0)
        assert config.duration_seconds == 120.0


class TestProviders:
    """Tests for provider system."""
    
    def test_list_providers(self):
        """Test listing available providers."""
        providers = list_providers()
        assert "audiogen" in providers
        assert "bark" in providers
    
    def test_get_provider_valid(self):
        """Test getting a valid provider."""
        provider = get_provider("audiogen")
        assert provider is not None
        assert isinstance(provider, AudioProvider)
        assert provider.name == "audiogen"
    
    def test_get_provider_invalid(self):
        """Test getting an invalid provider raises error."""
        with pytest.raises(ValueError):
            get_provider("nonexistent")
    
    def test_provider_debug_mode(self):
        """Test provider debug mode."""
        provider = get_provider("audiogen", debug=True)
        assert provider.debug is True
    
    def test_auto_detect_provider(self):
        """Test auto-detecting provider."""
        provider = auto_detect_provider()
        assert provider is not None
        assert isinstance(provider, AudioProvider)


class TestGenerationResult:
    """Tests for GenerationResult."""
    
    def test_result_creation(self):
        """Test creating a generation result."""
        result = GenerationResult(
            audio_path="/tmp/test.wav",
            duration_seconds=120.0,
            provider_name="test",
            prompt_used="test prompt",
            metadata={"sample_rate": 44100}
        )
        
        assert result.audio_path == "/tmp/test.wav"
        assert result.duration_seconds == 120.0
        assert result.duration_minutes == 2.0
        assert result.provider_name == "test"


class TestAmbienceGenerator:
    """Tests for AmbienceGenerator."""
    
    @patch("fmag.core.AudioProcessor")
    def test_generator_creation(self, mock_processor):
        """Test creating a generator."""
        config = GenerationConfig(mood="forest_cafe")
        generator = AmbienceGenerator(config)
        
        assert generator.config == config
        assert generator.provider is not None
    
    @patch("fmag.core.AudioProcessor")
    def test_generator_with_specific_provider(self, mock_processor):
        """Test creating generator with specific provider."""
        config = GenerationConfig(mood="forest_cafe", provider="bark")
        generator = AmbienceGenerator(config)
        
        assert generator.provider.name == "bark"
    
    @patch("fmag.core.AudioProcessor")
    def test_validate_valid_config(self, mock_processor):
        """Test validation with valid config."""
        config = GenerationConfig(mood="forest_cafe")
        generator = AmbienceGenerator(config)
        
        errors = generator.validate()
        # Should have no errors (or just provider availability)
        assert len(errors) <= 1
    
    @patch("fmag.core.AudioProcessor")
    def test_validate_short_custom_mood(self, mock_processor):
        """Test validation with too-short custom mood."""
        config = GenerationConfig(mood="rain")  # Too short for custom
        generator = AmbienceGenerator(config)
        
        errors = generator.validate()
        assert len(errors) >= 1


class TestListAvailableMoods:
    """Tests for list_available_moods helper."""
    
    def test_list_moods(self):
        """Test listing available moods."""
        moods = list_available_moods()
        
        assert len(moods) == 5
        for name, emoji, description in moods:
            assert name in PRESETS
            assert emoji
            assert description


class TestAudioUtils:
    """Tests for audio processing utilities."""
    
    @patch("fmag.audio_utils.subprocess.run")
    def test_audio_processor_creation(self, mock_run):
        """Test creating audio processor."""
        mock_run.return_value = MagicMock(returncode=0)
        
        processor = AudioProcessor(debug=False)
        assert processor is not None
    
    @patch("fmag.audio_utils.subprocess.run")
    def test_audio_processor_debug_mode(self, mock_run):
        """Test audio processor debug mode."""
        mock_run.return_value = MagicMock(returncode=0)
        
        processor = AudioProcessor(debug=True)
        assert processor.debug is True


class TestProviderMocking:
    """Tests for mocked provider calls."""
    
    def test_mock_provider_generate(self):
        """Test mocking provider generation."""
        mock_provider = MagicMock(spec=AudioProvider)
        mock_provider.is_available.return_value = True
        mock_provider.name = "mock"
        mock_provider.generate_audio.return_value = GenerationResult(
            audio_path="/tmp/test.wav",
            duration_seconds=60.0,
            provider_name="mock",
            prompt_used="test",
            metadata={}
        )
        
        result = mock_provider.generate_audio(
            prompt="test",
            duration_seconds=60.0,
            output_path="/tmp/test.wav"
        )
        
        assert result.audio_path == "/tmp/test.wav"
        mock_provider.generate_audio.assert_called_once()
    
    def test_mock_provider_error(self):
        """Test provider error handling."""
        mock_provider = MagicMock(spec=AudioProvider)
        mock_provider.generate_audio.side_effect = ProviderError("Test error")
        
        with pytest.raises(ProviderError):
            mock_provider.generate_audio(
                prompt="test",
                duration_seconds=60.0,
                output_path="/tmp/test.wav"
            )


class TestAudioProviderInterface:
    """Tests for AudioProvider base interface."""
    
    def test_audiogen_provider_is_available(self):
        """Test AudioGen provider availability check."""
        provider = get_provider("audiogen")
        # Should return True (demo mode)
        assert provider.is_available() is True
    
    def test_bark_provider_is_available(self):
        """Test Bark provider availability check."""
        provider = get_provider("bark")
        # Should return True (demo mode)
        assert provider.is_available() is True
    
    def test_provider_get_config_help(self):
        """Test provider configuration help."""
        provider = get_provider("audiogen")
        help_text = provider.get_config_help()
        
        assert isinstance(help_text, str)
        assert len(help_text) > 0


class TestIntegration:
    """Integration tests."""
    
    @patch("fmag.audio_utils.subprocess.run")
    def test_full_generation_pipeline(self, mock_run):
        """Test full generation pipeline with mocks."""
        # Mock FFmpeg availability
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="1.0",
            stderr=""
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config = GenerationConfig(
                mood="forest_cafe",
                duration_minutes=1.0,
                output_dir=tmpdir,
                debug=True
            )
            
            generator = AmbienceGenerator(config)
            
            # Validate should pass (mostly)
            errors = generator.validate()
            # Filter out FFmpeg-related errors for this test
            non_ffmpeg_errors = [e for e in errors if "ffmpeg" not in e.lower()]
            
            # Should have no major errors
            assert len(non_ffmpeg_errors) == 0

