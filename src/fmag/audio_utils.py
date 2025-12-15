"""
Audio utilities for processing and optimizing generated ambience.

Handles volume normalization, fading, and loop optimization
to create seamless, high-quality ambient soundscapes.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from rich.console import Console

console = Console()


class AudioProcessor:
    """Processes audio files for optimal loop playback."""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self._check_ffmpeg()
    
    def _check_ffmpeg(self) -> None:
        """Verify FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=True
            )
            if self.debug:
                console.print("[dim]FFmpeg found[/dim]")
        except FileNotFoundError:
            raise RuntimeError(
                "FFmpeg not found. Please install FFmpeg:\n"
                "  macOS: brew install ffmpeg\n"
                "  Ubuntu: sudo apt install ffmpeg\n"
                "  Windows: choco install ffmpeg"
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"FFmpeg error: {e.stderr}")
    
    def _run_ffmpeg(self, args: list[str]) -> None:
        """Run an FFmpeg command with error handling."""
        cmd = ["ffmpeg", "-y"] + args
        if self.debug:
            console.print(f"[dim]Running: {' '.join(cmd)}[/dim]")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            if self.debug:
                console.print(f"[red]FFmpeg error: {result.stderr}[/red]")
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
    
    def normalize_volume(
        self, 
        input_path: str, 
        output_path: str,
        target_loudness: float = -16.0
    ) -> str:
        """
        Normalize audio volume to target loudness (LUFS).
        
        Args:
            input_path: Path to input audio file
            output_path: Path for normalized output
            target_loudness: Target loudness in LUFS (default -16)
        
        Returns:
            Path to normalized audio file
        """
        # First pass: analyze loudness
        analyze_args = [
            "-i", input_path,
            "-af", f"loudnorm=I={target_loudness}:TP=-1.5:LRA=11:print_format=json",
            "-f", "null", "-"
        ]
        
        # For simplicity, use single-pass normalization
        normalize_args = [
            "-i", input_path,
            "-af", f"loudnorm=I={target_loudness}:TP=-1.5:LRA=11",
            "-ar", "44100",
            "-b:a", "192k",
            output_path
        ]
        
        self._run_ffmpeg(normalize_args)
        
        if self.debug:
            console.print(f"[green]✓[/green] Volume normalized to {target_loudness} LUFS")
        
        return output_path
    
    def apply_fades(
        self,
        input_path: str,
        output_path: str,
        fade_in_duration: float = 0.5,
        fade_out_duration: float = 0.5
    ) -> str:
        """
        Apply fade-in and fade-out effects.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output with fades
            fade_in_duration: Fade-in duration in seconds
            fade_out_duration: Fade-out duration in seconds
        
        Returns:
            Path to processed audio file
        """
        # Get audio duration first
        duration = self._get_duration(input_path)
        fade_out_start = duration - fade_out_duration
        
        fade_args = [
            "-i", input_path,
            "-af", (
                f"afade=t=in:st=0:d={fade_in_duration},"
                f"afade=t=out:st={fade_out_start}:d={fade_out_duration}"
            ),
            "-b:a", "192k",
            output_path
        ]
        
        self._run_ffmpeg(fade_args)
        
        if self.debug:
            console.print(
                f"[green]✓[/green] Applied fades: "
                f"in={fade_in_duration}s, out={fade_out_duration}s"
            )
        
        return output_path
    
    def optimize_for_loop(
        self,
        input_path: str,
        output_path: str,
        crossfade_duration: float = 1.0
    ) -> str:
        """
        Optimize audio for seamless looping with crossfade.
        
        Creates a smooth transition between the end and beginning
        of the audio for perfect loop playback.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for loop-optimized output
            crossfade_duration: Duration of crossfade in seconds
        
        Returns:
            Path to loop-optimized audio file
        """
        duration = self._get_duration(input_path)
        
        if duration < crossfade_duration * 2:
            # Audio too short for crossfade, just copy
            self._run_ffmpeg(["-i", input_path, "-c", "copy", output_path])
            return output_path
        
        # Create a crossfaded loop by:
        # 1. Taking the end portion
        # 2. Crossfading it with the beginning
        # 3. Reconstructing the full audio
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extract end portion for crossfade
            end_portion = os.path.join(tmpdir, "end.wav")
            start_time = duration - crossfade_duration
            
            self._run_ffmpeg([
                "-i", input_path,
                "-ss", str(start_time),
                "-t", str(crossfade_duration),
                end_portion
            ])
            
            # Extract beginning for crossfade
            begin_portion = os.path.join(tmpdir, "begin.wav")
            self._run_ffmpeg([
                "-i", input_path,
                "-t", str(crossfade_duration),
                begin_portion
            ])
            
            # Create crossfaded portion
            crossfade_out = os.path.join(tmpdir, "crossfade.wav")
            self._run_ffmpeg([
                "-i", end_portion,
                "-i", begin_portion,
                "-filter_complex",
                f"acrossfade=d={crossfade_duration}:c1=tri:c2=tri",
                crossfade_out
            ])
            
            # Extract middle portion
            middle_portion = os.path.join(tmpdir, "middle.wav")
            self._run_ffmpeg([
                "-i", input_path,
                "-ss", str(crossfade_duration),
                "-t", str(duration - crossfade_duration * 2),
                middle_portion
            ])
            
            # Concatenate: crossfade + middle
            concat_list = os.path.join(tmpdir, "concat.txt")
            with open(concat_list, "w") as f:
                f.write(f"file '{crossfade_out}'\n")
                f.write(f"file '{middle_portion}'\n")
            
            self._run_ffmpeg([
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list,
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                output_path
            ])
        
        if self.debug:
            console.print(
                f"[green]✓[/green] Loop optimized with {crossfade_duration}s crossfade"
            )
        
        return output_path
    
    def _get_duration(self, file_path: str) -> float:
        """Get the duration of an audio file in seconds."""
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                file_path
            ],
            capture_output=True,
            text=True,
            check=True
        )
        return float(result.stdout.strip())
    
    def process_full_pipeline(
        self,
        input_path: str,
        output_path: str,
        normalize: bool = True,
        fade_in: float = 0.5,
        fade_out: float = 0.5,
        loop_optimize: bool = True,
        crossfade: float = 1.0
    ) -> str:
        """
        Run the full audio processing pipeline.
        
        Args:
            input_path: Path to raw generated audio
            output_path: Final output path
            normalize: Whether to normalize volume
            fade_in: Fade-in duration (0 to disable)
            fade_out: Fade-out duration (0 to disable)
            loop_optimize: Whether to optimize for looping
            crossfade: Crossfade duration for loop optimization
        
        Returns:
            Path to fully processed audio file
        """
        current_path = input_path
        
        with tempfile.TemporaryDirectory() as tmpdir:
            step = 0
            
            if normalize:
                step += 1
                next_path = os.path.join(tmpdir, f"step{step}_normalized.wav")
                current_path = self.normalize_volume(current_path, next_path)
            
            if fade_in > 0 or fade_out > 0:
                step += 1
                next_path = os.path.join(tmpdir, f"step{step}_faded.wav")
                current_path = self.apply_fades(
                    current_path, next_path,
                    fade_in_duration=fade_in,
                    fade_out_duration=fade_out
                )
            
            if loop_optimize:
                step += 1
                next_path = os.path.join(tmpdir, f"step{step}_looped.wav")
                current_path = self.optimize_for_loop(
                    current_path, next_path,
                    crossfade_duration=crossfade
                )
            
            # Final export to MP3
            self._run_ffmpeg([
                "-i", current_path,
                "-c:a", "libmp3lame",
                "-b:a", "192k",
                "-ar", "44100",
                output_path
            ])
        
        return output_path


def check_ffmpeg_installed() -> bool:
    """Check if FFmpeg is installed on the system."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        return False

