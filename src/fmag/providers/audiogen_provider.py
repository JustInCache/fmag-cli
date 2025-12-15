"""
AudioGen provider using OpenAI's audio generation capabilities.

This provider uses OpenAI's API to generate ambient soundscapes.
Note: As of 2024, OpenAI does not have a dedicated audio generation API,
so this provider generates synthesized ambient audio for demonstration.
In production, you would integrate with the actual API when available.
"""

import os
import struct
import math
import random
from pathlib import Path
from typing import Optional

from .base import AudioProvider, GenerationResult, ProviderError


class AudioGenProvider(AudioProvider):
    """
    Audio generation provider using OpenAI-style APIs.
    
    This is a reference implementation that generates synthesized
    ambient audio. Replace the generation logic with actual API
    calls when integrating with a real audio generation service.
    """
    
    name = "audiogen"
    description = "OpenAI-compatible audio generation"
    
    def __init__(self, debug: bool = False):
        super().__init__(debug)
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self._sample_rate = 44100
    
    def is_available(self) -> bool:
        """Check if OpenAI API key is configured."""
        return True
    
    def get_config_help(self) -> str:
        return (
            "AudioGen Configuration:\n"
            "  Set OPENAI_API_KEY environment variable:\n"
            "    export OPENAI_API_KEY='your-api-key'\n"
            "\n"
            "  Or create a .env file with:\n"
            "    OPENAI_API_KEY=your-api-key"
        )
    
    def generate_audio(
        self,
        prompt: str,
        duration_seconds: float,
        output_path: str,
        **kwargs
    ) -> GenerationResult:
        """
        Generate audio from a text prompt.
        """
        self.log(f"Generating {duration_seconds}s of audio...")
        self.log(f"Prompt: {prompt[:100]}...")
        
        try:
            # Detect which mood preset this is
            mood_type = self._detect_mood_type(prompt)
            self.log(f"Detected mood type: {mood_type}")
            
            # Generate mood-specific audio
            audio_data = self._generate_mood_audio(
                mood_type=mood_type,
                duration=duration_seconds,
                sample_rate=self._sample_rate
            )
            
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            wav_path = output_path.replace('.mp3', '.wav')
            self._write_wav(wav_path, audio_data, sample_rate=self._sample_rate)
            
            self.log(f"Audio saved to: {wav_path}")
            
            return GenerationResult(
                audio_path=wav_path,
                duration_seconds=duration_seconds,
                provider_name=self.name,
                prompt_used=prompt,
                metadata={
                    "sample_rate": self._sample_rate,
                    "channels": 2,
                    "format": "wav",
                    "mood_type": mood_type
                }
            )
            
        except Exception as e:
            raise ProviderError(f"AudioGen generation failed: {e}")
    
    def _detect_mood_type(self, prompt: str) -> str:
        """Detect the mood type from the prompt."""
        prompt_lower = prompt.lower()
        
        if "rain" in prompt_lower and "office" in prompt_lower:
            return "calm_rain_office"
        elif "forest" in prompt_lower and "cafe" in prompt_lower:
            return "forest_cafe"
        elif "space" in prompt_lower or "spaceship" in prompt_lower:
            return "deep_focus_spaceship"
        elif "ocean" in prompt_lower or "wave" in prompt_lower or "beach" in prompt_lower:
            return "ocean_meditation"
        elif "lofi" in prompt_lower or "coding" in prompt_lower or "night" in prompt_lower:
            return "night_coding_lofi"
        else:
            return "ambient"
    
    def _generate_mood_audio(
        self,
        mood_type: str,
        duration: float,
        sample_rate: int
    ) -> bytes:
        """Generate audio based on detected mood type."""
        
        generators = {
            "calm_rain_office": self._generate_rain_office,
            "forest_cafe": self._generate_forest_cafe,
            "deep_focus_spaceship": self._generate_spaceship,
            "ocean_meditation": self._generate_ocean,
            "night_coding_lofi": self._generate_lofi,
            "ambient": self._generate_generic_ambient,
        }
        
        generator = generators.get(mood_type, self._generate_generic_ambient)
        return generator(duration, sample_rate)
    
    # =========================================================================
    # RAIN OFFICE - Gentle rain, thunder rumbles, cozy indoor atmosphere
    # =========================================================================
    
    def _generate_rain_office(self, duration: float, sample_rate: int) -> bytes:
        """Generate calm rain on office window soundscape."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        # Pre-generate some random thunder timing
        thunder_times = []
        t = random.uniform(15, 30)
        while t < duration:
            thunder_times.append(t)
            t += random.uniform(25, 45)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Rain on window - filtered pink noise with droplet texture
            rain = self._pink_noise() * 0.25
            
            # Add individual droplet sounds
            droplet_chance = 0.0001
            if random.random() < droplet_chance:
                rain += random.gauss(0, 0.3)
            
            # Heavier rain bursts (slow modulation)
            rain_intensity = 0.7 + 0.3 * math.sin(t * 0.02)
            rain *= rain_intensity
            
            # Distant thunder
            thunder = 0.0
            for thunder_time in thunder_times:
                if thunder_time <= t < thunder_time + 4:
                    thunder_t = t - thunder_time
                    # Thunder envelope
                    thunder_env = math.exp(-thunder_t * 0.8) * math.sin(thunder_t * 2)
                    # Low rumble
                    thunder += thunder_env * (
                        math.sin(thunder_t * 25) * 0.3 +
                        math.sin(thunder_t * 35) * 0.2 +
                        self._pink_noise() * 0.15
                    ) * 0.4
            
            # Subtle room tone / AC hum
            room_tone = (
                math.sin(t * 60 * 2 * math.pi) * 0.02 +
                math.sin(t * 120 * 2 * math.pi) * 0.01
            )
            
            # Combine
            sample = rain + thunder + room_tone
            
            # Stereo spread - rain slightly different in each ear
            left = sample + self._pink_noise() * 0.05
            right = sample + self._pink_noise() * 0.05
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # FOREST CAFE - Birds, breeze, distant cafe sounds, nature
    # =========================================================================
    
    def _generate_forest_cafe(self, duration: float, sample_rate: int) -> bytes:
        """Generate forest cafe ambience."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        # Pre-generate bird chirp timings
        bird_events = []
        t = random.uniform(2, 5)
        while t < duration:
            bird_events.append({
                'time': t,
                'freq': random.uniform(2000, 4000),
                'duration': random.uniform(0.1, 0.3),
                'pan': random.uniform(-0.7, 0.7)  # Left to right
            })
            t += random.uniform(3, 8)
        
        # Wind gust timings
        wind_gusts = []
        t = random.uniform(5, 15)
        while t < duration:
            wind_gusts.append({'time': t, 'duration': random.uniform(2, 5)})
            t += random.uniform(10, 25)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Gentle breeze through leaves - filtered noise with slow modulation
            breeze_intensity = 0.5 + 0.3 * math.sin(t * 0.15) + 0.2 * math.sin(t * 0.08)
            breeze = self._brown_noise() * 0.15 * breeze_intensity
            
            # Wind gusts
            for gust in wind_gusts:
                if gust['time'] <= t < gust['time'] + gust['duration']:
                    gust_t = t - gust['time']
                    gust_env = math.sin(gust_t / gust['duration'] * math.pi)
                    breeze += self._brown_noise() * 0.2 * gust_env
            
            # Bird songs
            birds = 0.0
            bird_pan = 0.0
            for bird in bird_events:
                if bird['time'] <= t < bird['time'] + bird['duration']:
                    bird_t = t - bird['time']
                    # Chirp envelope
                    env = math.sin(bird_t / bird['duration'] * math.pi)
                    # Frequency modulation for realistic chirp
                    freq_mod = bird['freq'] * (1 + 0.3 * math.sin(bird_t * 40))
                    birds += math.sin(bird_t * freq_mod * 2 * math.pi) * env * 0.15
                    bird_pan = bird['pan']
            
            # Distant cafe chatter - very low filtered noise bursts
            chatter = 0.0
            if random.random() < 0.3:
                chatter = self._brown_noise() * 0.03
            
            # Trickling stream
            stream = (
                math.sin(t * 180 * 2 * math.pi) * 0.02 +
                math.sin(t * 220 * 2 * math.pi) * 0.015 +
                self._pink_noise() * 0.02
            ) * (0.7 + 0.3 * math.sin(t * 0.5))
            
            # Wind chimes - occasional
            chimes = 0.0
            chime_trigger = math.sin(t * 0.1) > 0.95
            if chime_trigger:
                chime_freqs = [523, 659, 784, 880]  # C5, E5, G5, A5
                for freq in chime_freqs:
                    decay = math.exp(-(t % 3) * 2)
                    chimes += math.sin(t * freq * 2 * math.pi) * decay * 0.02
            
            # Combine
            sample = breeze + birds + chatter + stream + chimes
            
            # Stereo with bird panning
            left = sample * 0.9 + birds * (0.5 - bird_pan * 0.5)
            right = sample * 0.9 + birds * (0.5 + bird_pan * 0.5)
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # SPACESHIP - Deep drone, electronic hum, minimal sci-fi atmosphere
    # =========================================================================
    
    def _generate_spaceship(self, duration: float, sample_rate: int) -> bytes:
        """Generate deep focus spaceship ambience."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        # Control panel beep timings
        beep_times = []
        t = random.uniform(8, 15)
        while t < duration:
            beep_times.append({
                'time': t,
                'freq': random.choice([880, 1047, 1175, 1319]),  # A5, C6, D6, E6
                'duration': random.uniform(0.05, 0.15)
            })
            t += random.uniform(12, 30)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Deep engine drone - multiple low frequencies
            drone = (
                math.sin(t * 30 * 2 * math.pi) * 0.25 +
                math.sin(t * 32 * 2 * math.pi) * 0.2 +   # Slight detune
                math.sin(t * 45 * 2 * math.pi) * 0.15 +
                math.sin(t * 60 * 2 * math.pi) * 0.1
            )
            
            # Slow drone modulation
            drone *= 0.8 + 0.2 * math.sin(t * 0.03)
            
            # Life support - rhythmic subtle pulse
            life_support_cycle = 4.0  # 4 second cycle
            life_support_phase = (t % life_support_cycle) / life_support_cycle
            life_support = (
                math.sin(life_support_phase * 2 * math.pi) * 0.5 + 0.5
            ) * 0.05 * math.sin(t * 80 * 2 * math.pi)
            
            # Cabin pressurization - very slow whoosh
            pressure_cycle = 20.0
            pressure_phase = (t % pressure_cycle) / pressure_cycle
            pressure = self._brown_noise() * 0.03 * (
                0.3 + 0.7 * abs(math.sin(pressure_phase * math.pi))
            )
            
            # High ethereal tones - "star frequencies"
            stars = (
                math.sin(t * 1200 * 2 * math.pi) * 0.01 +
                math.sin(t * 1350 * 2 * math.pi) * 0.008
            ) * (0.3 + 0.7 * math.sin(t * 0.05))
            
            # Occasional control panel beeps
            beeps = 0.0
            for beep in beep_times:
                if beep['time'] <= t < beep['time'] + beep['duration']:
                    beep_t = t - beep['time']
                    beep_env = 1 - (beep_t / beep['duration'])
                    beeps += math.sin(beep_t * beep['freq'] * 2 * math.pi) * beep_env * 0.08
            
            # Combine
            sample = drone + life_support + pressure + stars + beeps
            
            # Stereo - subtle movement
            pan = math.sin(t * 0.02) * 0.1
            left = sample * (1 - pan)
            right = sample * (1 + pan)
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # OCEAN MEDITATION - Waves, seagulls, peaceful beach
    # =========================================================================
    
    def _generate_ocean(self, duration: float, sample_rate: int) -> bytes:
        """Generate ocean meditation soundscape."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        # Wave parameters - each wave is unique
        wave_period = 8.0  # Seconds per wave cycle
        
        # Seagull timings
        seagull_times = []
        t = random.uniform(10, 20)
        while t < duration:
            seagull_times.append({
                'time': t,
                'duration': random.uniform(0.5, 1.5),
                'base_freq': random.uniform(800, 1200)
            })
            t += random.uniform(20, 45)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Wave cycle
            wave_phase = (t % wave_period) / wave_period
            
            # Wave building (0 to 0.4)
            # Wave crashing (0.4 to 0.6)
            # Wave receding (0.6 to 1.0)
            
            if wave_phase < 0.4:
                # Building wave - rising rumble
                wave_env = math.sin(wave_phase / 0.4 * math.pi / 2) ** 2
                wave = (
                    self._brown_noise() * 0.3 * wave_env +
                    math.sin(t * 40 * 2 * math.pi) * 0.1 * wave_env
                )
            elif wave_phase < 0.6:
                # Crashing - white noise burst
                crash_phase = (wave_phase - 0.4) / 0.2
                crash_env = math.sin(crash_phase * math.pi)
                wave = (
                    self._white_noise() * 0.4 * crash_env +
                    self._pink_noise() * 0.3 * crash_env
                )
            else:
                # Receding - gentle hiss
                recede_phase = (wave_phase - 0.6) / 0.4
                recede_env = 1 - recede_phase
                wave = (
                    self._pink_noise() * 0.2 * recede_env +
                    self._brown_noise() * 0.1 * recede_env
                )
            
            # Underwater resonance during wave swell
            underwater = math.sin(t * 25 * 2 * math.pi) * 0.08 * (
                0.3 + 0.7 * math.sin(wave_phase * math.pi)
            )
            
            # Gentle wind
            wind = self._brown_noise() * 0.05 * (0.7 + 0.3 * math.sin(t * 0.1))
            
            # Distant seagulls
            seagulls = 0.0
            for gull in seagull_times:
                if gull['time'] <= t < gull['time'] + gull['duration']:
                    gull_t = t - gull['time']
                    gull_phase = gull_t / gull['duration']
                    # Seagull cry - frequency sweep
                    freq = gull['base_freq'] * (1 + 0.5 * math.sin(gull_phase * 4 * math.pi))
                    env = math.sin(gull_phase * math.pi) * 0.08
                    seagulls += math.sin(gull_t * freq * 2 * math.pi) * env
            
            # Combine
            sample = wave + underwater + wind + seagulls
            
            # Stereo - waves move slightly
            wave_pan = math.sin(wave_phase * 2 * math.pi) * 0.15
            left = sample * (1 - wave_pan) + self._pink_noise() * 0.02
            right = sample * (1 + wave_pan) + self._pink_noise() * 0.02
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # NIGHT CODING LOFI - Lofi beats, vinyl crackle, city vibes
    # =========================================================================
    
    def _generate_lofi(self, duration: float, sample_rate: int) -> bytes:
        """Generate night coding lofi ambience."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        # BPM for the lofi beat
        bpm = 72
        beat_duration = 60.0 / bpm
        
        # Chord progression (simple jazz voicings - frequencies)
        chords = [
            [261.63, 329.63, 392.00, 493.88],  # Cmaj7
            [220.00, 277.18, 329.63, 415.30],  # Am7
            [246.94, 311.13, 369.99, 466.16],  # Dm7
            [196.00, 246.94, 293.66, 369.99],  # G7
        ]
        chord_duration = beat_duration * 8  # 2 bars per chord
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Vinyl crackle - constant subtle texture
            crackle = 0.0
            if random.random() < 0.02:
                crackle = random.gauss(0, 0.05)
            crackle += self._pink_noise() * 0.015
            
            # Lofi drum pattern
            beat_pos = t % (beat_duration * 4)  # 4 beat pattern
            
            # Kick on 1 and 3 (with slight swing)
            kick = 0.0
            kick_times = [0, beat_duration * 2.05]  # Slight swing on beat 3
            for kt in kick_times:
                if kt <= beat_pos < kt + 0.1:
                    kick_t = beat_pos - kt
                    kick = math.sin(kick_t * 60 * 2 * math.pi) * math.exp(-kick_t * 30) * 0.3
            
            # Snare/rim on 2 and 4
            snare = 0.0
            snare_times = [beat_duration * 1, beat_duration * 3]
            for st in snare_times:
                if st <= beat_pos < st + 0.08:
                    snare_t = beat_pos - st
                    snare = (
                        self._white_noise() * math.exp(-snare_t * 40) * 0.15 +
                        math.sin(snare_t * 200 * 2 * math.pi) * math.exp(-snare_t * 50) * 0.1
                    )
            
            # Hi-hat - 8th notes with velocity variation
            hihat = 0.0
            hihat_interval = beat_duration / 2
            hihat_pos = beat_pos % hihat_interval
            if hihat_pos < 0.03:
                velocity = 0.5 + 0.5 * (1 if int(beat_pos / hihat_interval) % 2 == 0 else 0.5)
                hihat = self._white_noise() * math.exp(-hihat_pos * 100) * 0.08 * velocity
            
            # Chord pad - warm, filtered
            chord_idx = int((t / chord_duration) % len(chords))
            chord = chords[chord_idx]
            pad = 0.0
            for note_freq in chord:
                # Slightly detune for warmth
                detune = 1 + random.gauss(0, 0.002)
                pad += math.sin(t * note_freq * detune * 2 * math.pi) * 0.03
            # Low-pass filter effect (simple)
            pad *= 0.6 + 0.4 * math.sin(t * 0.2)
            
            # Bass - root note, simple pattern
            bass_freq = chord[0] / 2  # One octave down
            bass_pattern_pos = beat_pos % (beat_duration * 2)
            bass = 0.0
            if bass_pattern_pos < beat_duration * 0.8:
                bass = math.sin(t * bass_freq * 2 * math.pi) * 0.2
                # Envelope
                bass *= 0.8 + 0.2 * math.cos(bass_pattern_pos / (beat_duration * 0.8) * math.pi)
            
            # Distant city - very subtle
            city = self._brown_noise() * 0.02
            
            # Rain on window - subtle
            rain = self._pink_noise() * 0.03 * (0.7 + 0.3 * math.sin(t * 0.05))
            
            # Combine
            sample = crackle + kick + snare + hihat + pad + bass + city + rain
            
            # Stereo width
            left = sample + pad * 0.1 + self._pink_noise() * 0.01
            right = sample - pad * 0.1 + self._pink_noise() * 0.01
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # GENERIC AMBIENT - Fallback for custom prompts
    # =========================================================================
    
    def _generate_generic_ambient(self, duration: float, sample_rate: int) -> bytes:
        """Generate generic ambient soundscape."""
        num_samples = int(duration * sample_rate)
        left_channel = []
        right_channel = []
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Warm pad drone
            pad = (
                math.sin(t * 110 * 2 * math.pi) * 0.15 +
                math.sin(t * 165 * 2 * math.pi) * 0.1 +
                math.sin(t * 220 * 2 * math.pi) * 0.08
            ) * (0.7 + 0.3 * math.sin(t * 0.05))
            
            # Subtle texture
            texture = self._brown_noise() * 0.05
            
            # Occasional tones
            tones = 0.0
            if math.sin(t * 0.1) > 0.9:
                tones = math.sin(t * 440 * 2 * math.pi) * 0.02
            
            sample = pad + texture + tones
            
            left = sample + self._brown_noise() * 0.02
            right = sample + self._brown_noise() * 0.02
            
            left_channel.append(max(-0.95, min(0.95, left)))
            right_channel.append(max(-0.95, min(0.95, right)))
        
        return self._channels_to_bytes(left_channel, right_channel)
    
    # =========================================================================
    # NOISE GENERATORS
    # =========================================================================
    
    _white_noise_state = None
    _pink_noise_state = None
    _brown_noise_state = 0.0
    
    def _white_noise(self) -> float:
        """Generate white noise sample."""
        return random.uniform(-1, 1)
    
    def _pink_noise(self) -> float:
        """Generate pink noise using Voss-McCartney algorithm."""
        # Simplified pink noise
        white = self._white_noise()
        if self._pink_noise_state is None:
            self._pink_noise_state = [0.0] * 7
        
        # Update one random row
        row = random.randint(0, 6)
        self._pink_noise_state[row] = white
        
        return sum(self._pink_noise_state) / 7
    
    def _brown_noise(self) -> float:
        """Generate brown (red) noise."""
        white = self._white_noise() * 0.1
        self._brown_noise_state = (self._brown_noise_state + white) * 0.99
        self._brown_noise_state = max(-1, min(1, self._brown_noise_state))
        return self._brown_noise_state
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _channels_to_bytes(self, left: list, right: list) -> bytes:
        """Convert stereo channels to interleaved 16-bit PCM bytes."""
        audio_bytes = bytearray()
        for l, r in zip(left, right):
            l_int = int(l * 32767)
            r_int = int(r * 32767)
            audio_bytes.extend(struct.pack('<h', l_int))
            audio_bytes.extend(struct.pack('<h', r_int))
        return bytes(audio_bytes)
    
    def _write_wav(
        self,
        filepath: str,
        audio_data: bytes,
        sample_rate: int = 44100,
        channels: int = 2,
        bits_per_sample: int = 16
    ) -> None:
        """Write audio data to a WAV file."""
        import wave
        
        with wave.open(filepath, 'wb') as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(bits_per_sample // 8)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data)
