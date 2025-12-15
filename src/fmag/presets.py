"""
Mood presets for ambience generation.

Each preset contains a carefully crafted description and generation hints
to produce the perfect focus-enhancing soundscape.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class MoodPreset:
    """A mood preset for ambience generation."""
    
    name: str
    description: str
    style_hints: str
    suggested_tempo: str
    intensity: str
    elements: list[str]
    color: str  # For Rich terminal styling
    emoji: str
    
    def to_prompt(self) -> str:
        """Convert preset to a generation prompt."""
        elements_str = ", ".join(self.elements)
        return (
            f"{self.description}. "
            f"Style: {self.style_hints}. "
            f"Key elements: {elements_str}. "
            f"Tempo: {self.suggested_tempo}. "
            f"Create a seamless, loop-friendly ambient soundscape."
        )


# =============================================================================
# PRESET LIBRARY
# =============================================================================

PRESETS: dict[str, MoodPreset] = {
    "calm_rain_office": MoodPreset(
        name="calm_rain_office",
        description="Gentle rain falling outside a cozy office window",
        style_hints="soft, atmospheric, minimal, calming",
        suggested_tempo="very slow",
        intensity="low",
        elements=[
            "soft rain on glass",
            "distant thunder rumbles",
            "subtle keyboard clicks",
            "quiet air conditioning hum",
            "occasional paper rustling"
        ],
        color="blue",
        emoji="🌧️"
    ),
    
    "forest_cafe": MoodPreset(
        name="forest_cafe",
        description="A peaceful cafe nestled in a forest clearing",
        style_hints="organic, warm, natural, inviting",
        suggested_tempo="slow",
        intensity="low-medium",
        elements=[
            "birdsong in trees",
            "gentle breeze through leaves",
            "distant cafe chatter",
            "coffee machine sounds",
            "wooden wind chimes",
            "stream trickling nearby"
        ],
        color="green",
        emoji="🌲"
    ),
    
    "deep_focus_spaceship": MoodPreset(
        name="deep_focus_spaceship",
        description="The quiet hum of a spacecraft drifting through deep space",
        style_hints="futuristic, minimal, droning, hypnotic",
        suggested_tempo="static",
        intensity="very low",
        elements=[
            "engine resonance",
            "life support systems",
            "subtle electronic pulses",
            "distant star frequencies",
            "cabin pressurization",
            "control panel beeps"
        ],
        color="cyan",
        emoji="🚀"
    ),
    
    "ocean_meditation": MoodPreset(
        name="ocean_meditation",
        description="Waves gently lapping on a secluded beach at sunset",
        style_hints="rhythmic, breathing, vast, peaceful",
        suggested_tempo="very slow (wave rhythm)",
        intensity="medium",
        elements=[
            "ocean waves",
            "seagulls in distance",
            "sand shifting",
            "gentle wind",
            "underwater resonance",
            "shell sounds"
        ],
        color="bright_blue",
        emoji="🌊"
    ),
    
    "night_coding_lofi": MoodPreset(
        name="night_coding_lofi",
        description="Late night coding session with lofi beats and city ambience",
        style_hints="chill, nostalgic, urban, focused",
        suggested_tempo="slow hip-hop beat",
        intensity="medium",
        elements=[
            "lofi hip-hop drums",
            "vinyl crackle",
            "jazz piano samples",
            "distant city traffic",
            "rain on window",
            "keyboard typing",
            "muted bass"
        ],
        color="magenta",
        emoji="🌙"
    ),
}


def get_preset(name: str) -> Optional[MoodPreset]:
    """Get a preset by name."""
    return PRESETS.get(name)


def list_presets() -> list[str]:
    """List all available preset names."""
    return list(PRESETS.keys())


def get_preset_choices() -> list[tuple[str, str]]:
    """Get preset choices formatted for CLI menus."""
    return [
        (f"{preset.emoji} {name}", name) 
        for name, preset in PRESETS.items()
    ]

