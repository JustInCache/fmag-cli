# 📝 FMAG Example Commands

A collection of example commands to get you started with FMAG CLI.

---

## 🎯 Basic Usage

### 1. Generate with Default Settings
```bash
fmag generate calm_rain_office
```
Creates a 2-minute ambient loop with rain sounds.

### 2. Specify Duration
```bash
fmag generate forest_cafe --duration 3
```
Creates a 3-minute forest cafe ambience.

### 3. Short Duration Flag
```bash
fmag generate ocean_meditation -d 5
```
Creates a 5-minute ocean meditation soundscape.

---

## 🔌 Provider Selection

### 4. Use AudioGen Provider
```bash
fmag generate night_coding_lofi --provider audiogen
```
Explicitly uses the AudioGen provider for generation.

### 5. Use Bark Provider
```bash
fmag generate deep_focus_spaceship --provider bark
```
Uses the open-source Bark model for generation.

### 6. Short Provider Flag
```bash
fmag generate forest_cafe -p bark -d 2
```
Combines short flags for provider and duration.

---

## 📁 Output Configuration

### 7. Custom Output Directory
```bash
fmag generate calm_rain_office --output ./my-sounds
```
Saves the generated audio to a custom directory.

### 8. Short Output Flag
```bash
fmag generate ocean_meditation -o ~/Music/ambience -d 3
```
Saves to your Music folder with 3-minute duration.

---

## 🎨 Custom Prompts

### 9. Zen Garden Ambience
```bash
fmag generate "peaceful zen garden with wind chimes, bamboo water fountain, and distant temple bells" -d 5
```
Creates a custom zen garden soundscape.

### 10. Cozy Winter Cabin
```bash
fmag generate "crackling fireplace in a winter cabin, gentle snowfall outside, warm and cozy atmosphere" --duration 4
```
Creates a winter cabin ambience.

---

## 🔧 Advanced Options

### 11. Debug Mode
```bash
fmag generate forest_cafe --debug
```
Shows detailed provider logs and processing steps.

### 12. No Fade Effects
```bash
fmag generate night_coding_lofi --no-fade
```
Disables fade-in and fade-out effects.

### 13. No Loop Optimization
```bash
fmag generate ocean_meditation --no-loop
```
Disables crossfade loop optimization.

### 14. Full Custom Configuration
```bash
fmag generate calm_rain_office \
  --duration 4 \
  --provider audiogen \
  --output ./focus-sessions \
  --debug \
  --no-fade
```
Full control over all generation parameters.

---

## 📋 Information Commands

### 15. List Available Moods
```bash
fmag moods
```
Displays all available mood presets with descriptions.

### 16. List Providers
```bash
fmag providers
```
Shows available audio providers and their status.

### 17. Show Version
```bash
fmag --version
```
Displays the FMAG version.

### 18. Show Help
```bash
fmag --help
fmag generate --help
```
Shows help for main command or generate subcommand.

---

## 🎮 Interactive Mode

### 19. Launch Interactive Mode
```bash
fmag
```
Launches the guided interactive mode for beginners.

### 20. Interactive Generate
```bash
fmag generate
```
Runs generate command which falls back to interactive mode if no mood is specified.

---

## 🔄 Playback Tips

After generating, play your ambient audio:

```bash
# macOS
afplay ./output/fmag-forest_cafe-*.mp3

# Loop playback (requires mpv)
mpv --loop ./output/fmag-forest_cafe-*.mp3

# VLC loop
vlc --loop ./output/fmag-forest_cafe-*.mp3

# ffplay (comes with FFmpeg)
ffplay -loop 0 ./output/fmag-forest_cafe-*.mp3
```

---

## 🎧 Workflow Examples

### Morning Focus Session
```bash
# Generate calm rain for morning work
fmag generate calm_rain_office -d 5 -o ~/Music/focus

# Play on loop while working
mpv --loop ~/Music/focus/fmag-calm_rain_office-*.mp3
```

### Deep Work Session
```bash
# Generate spaceship ambience for intense focus
fmag generate deep_focus_spaceship --duration 5

# Play without distractions
afplay ./output/fmag-deep_focus_spaceship-*.mp3
```

### Evening Coding Session
```bash
# Generate lofi vibes for evening coding
fmag generate night_coding_lofi -d 4 -p audiogen

# Loop for extended session
mpv --loop ./output/fmag-night_coding_lofi-*.mp3
```

---

Happy focusing! 🎧✨

