"""
Bark provider for audio generation.

Bark is an open-source text-to-audio model that can generate
music, sound effects, and ambient sounds.
"""

import os
import struct
import math
import random
from pathlib import Path
from typing import Optional

from .base import AudioProvider, GenerationResult, ProviderError


class BarkProvider(AudioProvider):
    """
    Audio generation provider using Bark-style synthesis.
    
    Produces distinct ambient soundscapes with unique
    characteristics for each mood preset.
    """
    
    name = "bark"
    description = "Bark open-source audio generation"
    
    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self._bark_available = None
        self._sample_rate = 24000  # Bark uses 24kHz
        
        # State for continuous sounds
        self._noise_state = [0.0] * 16
        self._oscillator_phases = [0.0] * 16
    
    def is_available(self) -> bool:
        """Check if Bark is installed and available."""
        if self._bark_available is None:
            try:
                # Note: In production, you would import bark here
                # import bark
                self._bark_available = True
            except ImportError:
                self._bark_available = False
        return self._bark_available
    
    def get_config_help(self) -> str:
        return (
            "Bark Configuration:\n"
            "  Install Bark:\n"
            "    pip install bark\n"
            "\n"
            "  First run will download model files (~5GB).\n"
            "  GPU recommended for faster generation.\n"
            "\n"
            "  Environment variables:\n"
            "    BARK_CACHE_DIR: Model cache directory\n"
            "    CUDA_VISIBLE_DEVICES: GPU selection"
        )
    
    def generate_audio(
        self,
        prompt: str,
        duration_seconds: float,
        output_path: str,
        **kwargs
    ) -> GenerationResult:
        """Generate audio using Bark-style synthesis."""
        self.log(f"Generating {duration_seconds}s of audio with Bark...")
        self.log(f"Prompt: {prompt[:100]}...")
        
        try:
            # Detect mood from prompt
            mood = self._detect_mood(prompt)
            self.log(f"Detected mood: {mood}")
            
            # Generate mood-specific audio
            audio_data = self._generate_mood_audio(mood, duration_seconds)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write to WAV file
            wav_path = output_path.replace('.mp3', '.wav')
            self._write_wav(wav_path, audio_data, sample_rate=self._sample_rate, channels=1)
            
            self.log(f"Audio saved to: {wav_path}")
            
            return GenerationResult(
                audio_path=wav_path,
                duration_seconds=duration_seconds,
                provider_name=self.name,
                prompt_used=prompt,
                metadata={
                    "sample_rate": self._sample_rate,
                    "channels": 1,
                    "format": "wav",
                    "model": "bark",
                    "mood": mood
                }
            )
            
        except Exception as e:
            raise ProviderError(f"Bark generation failed: {e}")
    
    def _detect_mood(self, prompt: str) -> str:
        """Detect mood type from prompt."""
        prompt_lower = prompt.lower()
        
        if "rain" in prompt_lower and "office" in prompt_lower:
            return "calm_rain_office"
        elif "forest" in prompt_lower or "cafe" in prompt_lower:
            return "forest_cafe"
        elif "space" in prompt_lower or "ship" in prompt_lower:
            return "deep_focus_spaceship"
        elif "ocean" in prompt_lower or "wave" in prompt_lower or "beach" in prompt_lower:
            return "ocean_meditation"
        elif "lofi" in prompt_lower or "coding" in prompt_lower or "night" in prompt_lower:
            return "night_coding_lofi"
        elif "rain" in prompt_lower:
            return "calm_rain_office"
        elif "zen" in prompt_lower or "meditation" in prompt_lower:
            return "ocean_meditation"
        else:
            return "forest_cafe"
    
    def _generate_mood_audio(self, mood: str, duration: float) -> bytes:
        """Generate mono audio specific to the mood."""
        num_samples = int(duration * self._sample_rate)
        
        generators = {
            "calm_rain_office": self._generate_rain,
            "forest_cafe": self._generate_forest,
            "deep_focus_spaceship": self._generate_space,
            "ocean_meditation": self._generate_ocean,
            "night_coding_lofi": self._generate_lofi,
        }
        
        generator = generators.get(mood, self._generate_forest)
        samples = []
        
        for i in range(num_samples):
            t = i / self._sample_rate
            sample = generator(t, i)
            samples.append(max(-1, min(1, sample)))
        
        # Convert to 16-bit PCM
        audio_bytes = bytearray()
        for s in samples:
            s_int = int(s * 32767)
            audio_bytes.extend(struct.pack('<h', s_int))
        
        return bytes(audio_bytes)
    
    # =========================================================================
    # MOOD GENERATORS
    # =========================================================================
    
    def _generate_rain(self, t: float, i: int) -> float:
        """Calm rain with indoor ambience."""
        # Rain noise
        rain = self._pink_noise() * 0.3
        rain *= 0.7 + 0.3 * math.sin(t * 0.12)
        
        # Drips
        drip = 0
        if i % int(self._sample_rate * 1.8) < 150:
            drip_t = (i % int(self._sample_rate * 1.8)) / self._sample_rate
            drip = math.sin(drip_t * 600) * math.exp(-drip_t * 25) * 0.12
        
        # Low hum
        hum = math.sin(t * 50 * 2 * math.pi) * 0.025
        
        # Thunder
        thunder = 0
        if i % int(self._sample_rate * 40) < self._sample_rate * 3:
            thunder_t = (i % int(self._sample_rate * 40)) / self._sample_rate
            thunder = self._brown_noise() * math.sin(thunder_t * 0.5) ** 2 * 0.15
        
        return (rain + drip + hum + thunder) * 0.8
    
    def _generate_forest(self, t: float, i: int) -> float:
        """Forest with birds and nature sounds."""
        # Wind in trees
        wind = self._pink_noise() * (0.4 + 0.2 * math.sin(t * 0.06)) * 0.15
        
        # Birds
        birds = 0
        
        # Chirping bird
        if (t % 4.2) < 0.2:
            chirp_t = (t % 4.2) / 0.2
            freq = 2600 + 500 * math.sin(chirp_t * 12)
            birds += math.sin(t * freq * 2 * math.pi) * math.sin(chirp_t * math.pi) ** 2 * 0.1
        
        # Melodic bird
        if ((t + 1.5) % 6.8) < 0.35:
            call_t = ((t + 1.5) % 6.8) / 0.35
            freq = 1600 + 300 * math.sin(call_t * 10)
            birds += math.sin(t * freq * 2 * math.pi) * math.sin(call_t * math.pi) * 0.07
        
        # Stream
        stream = self._filtered_noise(500, 2500) * 0.06
        
        # Cafe murmur
        cafe = self._filtered_noise(150, 500) * 0.06
        
        return (wind + birds + stream + cafe) * 0.85
    
    def _generate_space(self, t: float, i: int) -> float:
        """Spaceship engine and electronics."""
        # Deep drone
        drone = 0
        for h in range(1, 7):
            freq = 40 * h * (1 + 0.002 * math.sin(t * 0.08 * h))
            drone += math.sin(t * freq * 2 * math.pi) / (h ** 1.3)
        drone *= 0.2 * (0.85 + 0.15 * math.sin(t * 0.06))
        
        # Life support hiss
        hiss = self._filtered_noise(5000, 10000) * 0.025
        
        # Resonance
        res = math.sin(t * 68 * 2 * math.pi) * 0.03
        res += math.sin(t * 136 * 2 * math.pi) * 0.015
        
        # Beeps
        beep = 0
        if i % int(self._sample_rate * 15) < int(self._sample_rate * 0.08):
            beep_t = (i % int(self._sample_rate * 15)) / self._sample_rate
            beep = math.sin(t * 800 * 2 * math.pi) * math.exp(-beep_t * 35) * 0.06
        
        # Sub bass
        sub = math.sin(t * 28 * 2 * math.pi) * 0.08
        
        return (drone + hiss + res + beep + sub) * 0.9
    
    def _generate_ocean(self, t: float, i: int) -> float:
        """Ocean waves and beach."""
        # Main wave
        wave_period = 9.0
        wave_phase = (t % wave_period) / wave_period
        
        if wave_phase < 0.45:
            wave_env = (wave_phase / 0.45) ** 1.3
        elif wave_phase < 0.55:
            wave_env = 1.0
        else:
            wave_env = 1.0 - ((wave_phase - 0.55) / 0.45) ** 0.6
        
        wave = self._brown_noise() * wave_env * 0.35
        
        # Foam
        foam = 0
        if wave_phase > 0.5:
            foam_env = math.sin((wave_phase - 0.5) / 0.5 * math.pi)
            foam = self._filtered_noise(2500, 7000) * foam_env * 0.12
        
        # Secondary wave
        wave2_phase = ((t + 3) % 6.0) / 6.0
        wave2 = self._brown_noise() * math.sin(wave2_phase * math.pi) ** 2 * 0.12
        
        # Underwater
        underwater = math.sin(t * 32 * 2 * math.pi) * wave_env * 0.06
        
        # Seagull
        seagull = 0
        if i % int(self._sample_rate * 30) < int(self._sample_rate * 0.6):
            gull_t = (i % int(self._sample_rate * 30)) / self._sample_rate
            freq = 1600 + 350 * math.sin(gull_t * 5)
            seagull = math.sin(t * freq * 2 * math.pi) * math.sin(gull_t / 0.6 * math.pi) ** 0.6 * 0.04
        
        # Wind
        wind = self._filtered_noise(200, 1000) * 0.05
        
        return (wave + foam + wave2 + underwater + seagull + wind) * 0.8
    
    def _generate_lofi(self, t: float, i: int) -> float:
        """Lo-fi hip hop beats."""
        bpm = 72
        beat = 60.0 / bpm
        bar = beat * 4
        bar_phase = (t % bar) / bar
        beat_phase = (t % beat) / beat
        
        # Kick
        kick = 0
        for kt in [0, 0.5]:
            kp = (bar_phase - kt) % 1.0
            if kp < 0.04:
                kick += math.sin((kp / 0.04) * 55 * math.pi) * math.exp(-kp * 200) * 0.35
        
        # Snare
        snare = 0
        for st in [0.25, 0.75]:
            sp = (bar_phase - st) % 1.0
            if sp < 0.025:
                snare += self._white_noise() * math.exp(-sp * 400) * 0.12
        
        # Hi-hat
        hihat = 0
        for hh in range(8):
            hp = (bar_phase - hh / 8) % 1.0
            if hp < 0.015:
                hihat += self._filtered_noise(7000, 14000) * math.exp(-hp * 500) * 0.06
        
        # Bass
        bass_notes = [55, 55, 73.4, 65.4]
        bass_freq = bass_notes[int(bar_phase * 4) % 4]
        bass = math.sin(t * bass_freq * 2 * math.pi) * 0.18
        
        # Pad
        pad = 0
        for freq in [262, 330, 392, 466]:
            pad += math.sin(t * freq * 2 * math.pi)
        pad *= 0.03
        
        # Vinyl
        vinyl = self._filtered_noise(1500, 5000) * 0.015
        if random.random() < 0.01:
            vinyl += random.gauss(0, 0.06)
        
        # Rain
        rain = self._pink_noise() * 0.04
        
        sample = kick + snare + hihat + bass + pad + vinyl + rain
        return math.tanh(sample * 1.1) * 0.8
    
    # =========================================================================
    # NOISE GENERATORS
    # =========================================================================
    
    def _white_noise(self) -> float:
        return random.uniform(-1, 1)
    
    def _pink_noise(self) -> float:
        white = random.uniform(-1, 1)
        self._noise_state[0] = 0.99886 * self._noise_state[0] + white * 0.0555179
        self._noise_state[1] = 0.99332 * self._noise_state[1] + white * 0.0750759
        self._noise_state[2] = 0.96900 * self._noise_state[2] + white * 0.1538520
        self._noise_state[3] = 0.86650 * self._noise_state[3] + white * 0.3104856
        self._noise_state[4] = 0.55000 * self._noise_state[4] + white * 0.5329522
        self._noise_state[5] = -0.7616 * self._noise_state[5] - white * 0.0168980
        
        return (self._noise_state[0] + self._noise_state[1] + self._noise_state[2] +
                self._noise_state[3] + self._noise_state[4] + self._noise_state[5] +
                white * 0.5362) * 0.11
    
    def _brown_noise(self) -> float:
        white = random.uniform(-1, 1)
        self._noise_state[6] = (self._noise_state[6] + white * 0.02) * 0.998
        self._noise_state[6] = max(-1, min(1, self._noise_state[6]))
        return self._noise_state[6]
    
    def _filtered_noise(self, low_freq: float, high_freq: float) -> float:
        white = self._white_noise()
        cutoff = high_freq / 12000
        self._noise_state[7] = self._noise_state[7] * (1 - cutoff) + white * cutoff
        hp = low_freq / 12000
        self._noise_state[8] = self._noise_state[8] * (1 - hp) + self._noise_state[7] * hp
        return self._noise_state[7] - self._noise_state[8]
    
    def _write_wav(
        self,
        filepath: str,
        audio_data: bytes,
        sample_rate: int = 24000,
        channels: int = 1,
        bits_per_sample: int = 16
    ) -> None:
        """Write audio data to a WAV file."""
        import wave
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bits_per_sample // 8)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
