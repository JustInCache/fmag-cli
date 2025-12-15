"""
Tests for FMAG CLI interface.
"""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from fmag.cli import app


runner = CliRunner()


class TestCLICommands:
    """Tests for CLI commands."""
    
    def test_version_flag(self):
        """Test --version flag shows version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "FMAG CLI" in result.stdout
        assert "v" in result.stdout
    
    def test_version_command(self):
        """Test version command."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "FMAG CLI" in result.stdout
    
    def test_moods_command(self):
        """Test moods command lists presets."""
        result = runner.invoke(app, ["moods"])
        assert result.exit_code == 0
        assert "calm_rain_office" in result.stdout
        assert "forest_cafe" in result.stdout
        assert "deep_focus_spaceship" in result.stdout
        assert "ocean_meditation" in result.stdout
        assert "night_coding_lofi" in result.stdout
    
    def test_providers_command(self):
        """Test providers command lists providers."""
        result = runner.invoke(app, ["providers"])
        assert result.exit_code == 0
        assert "audiogen" in result.stdout
        assert "bark" in result.stdout
    
    def test_generate_help(self):
        """Test generate command help."""
        result = runner.invoke(app, ["generate", "--help"])
        assert result.exit_code == 0
        assert "--duration" in result.stdout
        assert "--provider" in result.stdout
        assert "--output" in result.stdout
        assert "--debug" in result.stdout


class TestGenerateCommand:
    """Tests for the generate command."""
    
    @patch("fmag.cli.check_ffmpeg_installed")
    @patch("fmag.cli.AmbienceGenerator")
    def test_generate_with_preset(self, mock_generator_class, mock_ffmpeg):
        """Test generate command with a preset mood."""
        mock_ffmpeg.return_value = True
        mock_generator = MagicMock()
        mock_generator.validate.return_value = []
        mock_generator.generate.return_value = "/output/test.mp3"
        mock_generator_class.return_value = mock_generator
        
        result = runner.invoke(app, [
            "generate", "forest_cafe",
            "--duration", "1"
        ])
        
        assert result.exit_code == 0
        assert "forest_cafe" in result.stdout or "Complete" in result.stdout
    
    @patch("fmag.cli.check_ffmpeg_installed")
    def test_generate_without_ffmpeg(self, mock_ffmpeg):
        """Test generate fails gracefully without FFmpeg."""
        mock_ffmpeg.return_value = False
        
        result = runner.invoke(app, ["generate", "forest_cafe"])
        
        assert result.exit_code == 1
        assert "FFmpeg" in result.stdout
    
    def test_generate_invalid_duration_low(self):
        """Test generate rejects duration below 1."""
        result = runner.invoke(app, [
            "generate", "forest_cafe",
            "--duration", "0.5"
        ])
        # Typer should reject this due to min constraint
        assert result.exit_code != 0 or "Invalid" in result.stdout or "Error" in result.stdout
    
    def test_generate_invalid_duration_high(self):
        """Test generate rejects duration above 5."""
        result = runner.invoke(app, [
            "generate", "forest_cafe",
            "--duration", "10"
        ])
        # Typer should reject this due to max constraint
        assert result.exit_code != 0 or "Invalid" in result.stdout or "Error" in result.stdout


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""
    
    def test_duration_short_flag(self):
        """Test -d flag works for duration."""
        result = runner.invoke(app, ["generate", "--help"])
        assert "-d" in result.stdout
        assert "--duration" in result.stdout
    
    def test_provider_short_flag(self):
        """Test -p flag works for provider."""
        result = runner.invoke(app, ["generate", "--help"])
        assert "-p" in result.stdout
        assert "--provider" in result.stdout
    
    def test_output_short_flag(self):
        """Test -o flag works for output."""
        result = runner.invoke(app, ["generate", "--help"])
        assert "-o" in result.stdout
        assert "--output" in result.stdout


class TestBanner:
    """Tests for CLI banner."""
    
    def test_banner_shown_on_moods(self):
        """Test banner is displayed on moods command."""
        result = runner.invoke(app, ["moods"])
        # Banner uses ASCII art, check for key elements
        assert "Focus Mode Ambience Generator" in result.stdout
    
    def test_banner_shown_on_providers(self):
        """Test banner is displayed on providers command."""
        result = runner.invoke(app, ["providers"])
        # Banner uses ASCII art, check for key elements
        assert "Focus Mode Ambience Generator" in result.stdout

