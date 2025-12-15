"""
FMAG CLI - Focus Mode Ambience Generator

Beautiful command-line interface for generating AI-powered
ambient soundscapes.
"""

import os
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich import box

from . import __version__
from .core import AmbienceGenerator, GenerationConfig, list_available_moods
from .presets import PRESETS, get_preset, list_presets
from .providers import list_providers
from .audio_utils import check_ffmpeg_installed

# Initialize CLI app
app = typer.Typer(
    name="fmag",
    help="🎧 Focus Mode Ambience Generator - AI-powered ambient soundscapes",
    add_completion=False,
    no_args_is_help=False,
)

console = Console()

# ============================================================================
# ASCII Art Banner
# ============================================================================

BANNER = """
[bold cyan]
    ███████╗███╗   ███╗ █████╗  ██████╗ 
    ██╔════╝████╗ ████║██╔══██╗██╔════╝ 
    █████╗  ██╔████╔██║███████║██║  ███╗
    ██╔══╝  ██║╚██╔╝██║██╔══██║██║   ██║
    ██║     ██║ ╚═╝ ██║██║  ██║╚██████╔╝
    ╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ 
[/bold cyan]
[dim]Focus Mode Ambience Generator v{version}[/dim]
[dim italic]AI-powered soundscapes for deep focus[/dim italic]
"""


def show_banner():
    """Display the FMAG banner."""
    console.print(BANNER.format(version=__version__))


# ============================================================================
# CLI Commands
# ============================================================================

@app.command()
def generate(
    mood: Optional[str] = typer.Argument(
        None,
        help="Mood preset name (e.g., calm_rain_office) or custom prompt"
    ),
    duration: float = typer.Option(
        2.0,
        "--duration", "-d",
        help="Duration in minutes (1-5)",
        min=1.0,
        max=5.0
    ),
    provider: Optional[str] = typer.Option(
        None,
        "--provider", "-p",
        help="Audio provider (audiogen, bark)"
    ),
    output_dir: str = typer.Option(
        "./output",
        "--output", "-o",
        help="Output directory for generated files"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Enable debug logging"
    ),
    no_fade: bool = typer.Option(
        False,
        "--no-fade",
        help="Disable fade in/out effects"
    ),
    no_loop: bool = typer.Option(
        False,
        "--no-loop",
        help="Disable loop optimization"
    ),
):
    """
    Generate ambient audio from a mood preset or custom prompt.
    
    Examples:
        fmag generate forest_cafe
        fmag generate night_coding_lofi --duration 3
        fmag generate "peaceful zen garden with wind chimes" -d 5
    """
    show_banner()
    
    # If no mood provided, launch interactive mode
    if mood is None:
        mood, duration, provider = interactive_mode()
        if mood is None:
            raise typer.Exit()
    
    # Check FFmpeg
    if not check_ffmpeg_installed():
        console.print(Panel(
            "[red]FFmpeg is required but not installed.[/red]\n\n"
            "Install FFmpeg:\n"
            "  [cyan]macOS:[/cyan]    brew install ffmpeg\n"
            "  [cyan]Ubuntu:[/cyan]   sudo apt install ffmpeg\n"
            "  [cyan]Windows:[/cyan]  choco install ffmpeg",
            title="⚠️  Missing Dependency",
            border_style="red"
        ))
        raise typer.Exit(1)
    
    # Show generation info
    preset = get_preset(mood)
    if preset:
        console.print(Panel(
            f"[bold]{preset.emoji} {preset.name}[/bold]\n\n"
            f"[dim]{preset.description}[/dim]",
            title="🎵 Selected Mood",
            border_style=preset.color
        ))
    else:
        console.print(Panel(
            f"[bold]🎵 Custom Prompt[/bold]\n\n"
            f"[dim]{mood}[/dim]",
            title="🎵 Custom Generation",
            border_style="magenta"
        ))
    
    console.print()
    console.print(f"[dim]Duration:[/dim] {duration} minutes")
    console.print(f"[dim]Provider:[/dim] {provider or 'auto-detect'}")
    console.print(f"[dim]Output:[/dim] {output_dir}/")
    console.print()
    
    # Create configuration
    config = GenerationConfig(
        mood=mood,
        duration_minutes=duration,
        provider=provider,
        output_dir=output_dir,
        debug=debug,
        fade_in=0 if no_fade else 0.5,
        fade_out=0 if no_fade else 0.5,
        loop_optimize=not no_loop,
    )
    
    # Generate
    try:
        generator = AmbienceGenerator(config)
        
        # Validate
        errors = generator.validate()
        if errors:
            for error in errors:
                console.print(f"[red]✗[/red] {error}")
            raise typer.Exit(1)
        
        # Generate audio
        output_path = generator.generate()
        
        # Success message
        console.print()
        console.print(Panel(
            f"[bold green]✓ Audio generated successfully![/bold green]\n\n"
            f"[dim]Saved to:[/dim] [cyan]{output_path}[/cyan]\n\n"
            f"[dim]Play with:[/dim]\n"
            f"  [yellow]afplay {output_path}[/yellow]  [dim](macOS)[/dim]\n"
            f"  [yellow]mpv --loop {output_path}[/yellow]  [dim](loop)[/dim]",
            title="🎉 Complete",
            border_style="green"
        ))
        
    except Exception as e:
        console.print(f"[red]✗ Generation failed:[/red] {e}")
        if debug:
            console.print_exception()
        raise typer.Exit(1)


@app.command()
def moods():
    """List all available mood presets."""
    show_banner()
    
    table = Table(
        title="🎨 Available Mood Presets",
        box=box.ROUNDED,
        header_style="bold cyan"
    )
    
    table.add_column("Mood", style="bold")
    table.add_column("Description", style="dim")
    table.add_column("Intensity", justify="center")
    
    for name, preset in PRESETS.items():
        table.add_row(
            f"{preset.emoji} {name}",
            preset.description,
            preset.intensity
        )
    
    console.print(table)
    console.print()
    console.print(
        "[dim]Use with:[/dim] "
        "[cyan]fmag generate <mood>[/cyan]"
    )


@app.command()
def providers():
    """List available audio providers."""
    show_banner()
    
    table = Table(
        title="🔌 Audio Providers",
        box=box.ROUNDED,
        header_style="bold cyan"
    )
    
    table.add_column("Provider", style="bold")
    table.add_column("Description")
    table.add_column("Status", justify="center")
    
    from .providers import get_provider
    
    for provider_name in list_providers():
        try:
            provider = get_provider(provider_name)
            status = "[green]✓ Available[/green]" if provider.is_available() else "[yellow]⚠ Setup needed[/yellow]"
            table.add_row(
                provider_name,
                provider.description,
                status
            )
        except Exception:
            table.add_row(
                provider_name,
                "Unknown",
                "[red]✗ Error[/red]"
            )
    
    console.print(table)
    console.print()
    console.print(
        "[dim]Use with:[/dim] "
        "[cyan]fmag generate <mood> --provider <name>[/cyan]"
    )


@app.command()
def version():
    """Show version information."""
    console.print(f"[bold cyan]FMAG CLI[/bold cyan] v{__version__}")


# ============================================================================
# Interactive Mode
# ============================================================================

def interactive_mode() -> tuple[Optional[str], float, Optional[str]]:
    """
    Launch interactive mode for guided generation.
    
    Returns:
        Tuple of (mood, duration, provider)
    """
    console.print(Panel(
        "[bold]Welcome to Interactive Mode![/bold]\n\n"
        "Let's create the perfect ambient soundscape for your focus session.",
        title="🎧 FMAG Interactive",
        border_style="cyan"
    ))
    console.print()
    
    # Mood selection
    console.print("[bold cyan]Step 1:[/bold cyan] Select a mood\n")
    
    for i, (name, preset) in enumerate(PRESETS.items(), 1):
        console.print(f"  [bold]{i}.[/bold] {preset.emoji} {name}")
        console.print(f"     [dim]{preset.description}[/dim]")
    console.print(f"  [bold]{len(PRESETS) + 1}.[/bold] 🎵 Custom prompt")
    console.print()
    
    mood_choice = IntPrompt.ask(
        "Select mood",
        default=1,
        choices=[str(i) for i in range(1, len(PRESETS) + 2)]
    )
    
    if mood_choice == len(PRESETS) + 1:
        mood = Prompt.ask("Enter custom prompt")
    else:
        mood = list(PRESETS.keys())[mood_choice - 1]
    
    console.print()
    
    # Duration selection
    console.print("[bold cyan]Step 2:[/bold cyan] Select duration\n")
    console.print("  [bold]1.[/bold] 1 minute  [dim](quick test)[/dim]")
    console.print("  [bold]2.[/bold] 2 minutes [dim](default)[/dim]")
    console.print("  [bold]3.[/bold] 3 minutes [dim](medium session)[/dim]")
    console.print("  [bold]4.[/bold] 5 minutes [dim](extended focus)[/dim]")
    console.print()
    
    duration_choice = IntPrompt.ask(
        "Select duration",
        default=2,
        choices=["1", "2", "3", "4"]
    )
    
    duration_map = {1: 1.0, 2: 2.0, 3: 3.0, 4: 5.0}
    duration = duration_map[duration_choice]
    
    console.print()
    
    # Provider selection
    console.print("[bold cyan]Step 3:[/bold cyan] Select provider\n")
    available_providers = list_providers()
    
    console.print("  [bold]1.[/bold] 🤖 Auto-detect [dim](recommended)[/dim]")
    for i, prov in enumerate(available_providers, 2):
        console.print(f"  [bold]{i}.[/bold] {prov}")
    console.print()
    
    provider_choice = IntPrompt.ask(
        "Select provider",
        default=1,
        choices=[str(i) for i in range(1, len(available_providers) + 2)]
    )
    
    if provider_choice == 1:
        provider = None
    else:
        provider = available_providers[provider_choice - 2]
    
    console.print()
    console.print("[bold green]✓[/bold green] Configuration complete!")
    console.print()
    
    return mood, duration, provider


# ============================================================================
# Main Entry Point
# ============================================================================

@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version_flag: bool = typer.Option(
        False,
        "--version", "-v",
        help="Show version and exit"
    ),
):
    """
    🎧 FMAG - Focus Mode Ambience Generator
    
    Generate AI-powered ambient soundscapes for deep focus.
    
    Run without arguments to enter interactive mode.
    """
    if version_flag:
        console.print(f"[bold cyan]FMAG CLI[/bold cyan] v{__version__}")
        raise typer.Exit()
    
    # If no subcommand provided, launch interactive generate
    if ctx.invoked_subcommand is None:
        show_banner()
        mood, duration, provider = interactive_mode()
        if mood:
            # Invoke generate with interactive values
            # Must pass all parameters to avoid OptionInfo objects being used
            ctx.invoke(
                generate,
                mood=mood,
                duration=duration,
                provider=provider,
                output_dir="./output",
                debug=False,
                no_fade=False,
                no_loop=False,
            )


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()

