from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text

# Your Cyber Blue Palette
PALETTE = {
    "white": "#ffffff",
    "cyan_bright": "#0ce6f2",
    "blue_vivid": "#0098db",
    "blue_mid": "#1e579c",
    "blue_dark": "#203562",
    "deep_navy": "#252446",
    "void": "#201533"
}

custom_theme = Theme({
    "info": f"{PALETTE['cyan_bright']}",
    "warning": "yellow",
    "error": "bold red",
    "success": f"bold {PALETTE['cyan_bright']}",
    "primary": f"bold {PALETTE['blue_vivid']}",
    "secondary": f"{PALETTE['blue_mid']}",
    "border": f"{PALETTE['blue_mid']}",
})

console = Console(theme=custom_theme)

def print_banner():
    """
    Displays the clean banner, single line, full width.
    No emojis here to ensure stability on Windows.
    """
    
    # Assemble only essential text
    banner_text = Text.assemble(
        ("GitScribe ", f"bold {PALETTE['white']}"),
        ("v0.2.0", f"dim {PALETTE['cyan_bright']}")
    )
    
    # Safe Full-Width Panel
    console.print(Panel(
        banner_text,
        style=f"{PALETTE['white']} on {PALETTE['deep_navy']}",
        border_style=PALETTE['blue_vivid'],
        title="[italic]AI-Powered Commit Tool[/italic]",
        title_align="right",
        expand=True,   # Safe to use expand=True with text only
        padding=(0, 1) # Minimum height (Single line)
    ))

def header(text: str):
    console.print(f"\n[{PALETTE['cyan_bright']}]║ {text}[/{PALETTE['cyan_bright']}]")

def step_status(msg: str, status: str = "wait"):
    icon = "⏳"
    color = PALETTE['blue_mid']
    
    if status == "done":
        icon = "✔"
        color = "green"
    elif status == "error":
        icon = "✖"
        color = "red"
        
    console.print(f"[{color}]{icon} {msg}[/{color}]")

def print_footer():
    """Exibe a assinatura discreta no final da execução."""
    # justify="right" move the text to the right corner
    console.print(f"\n[{PALETTE['blue_dark']}]Made by Patro[/]", justify="right")

def print_commit_link(url: str):
    """Exibe o link do commit formatado e clicável."""
    # O [link=URL]texto[/link] faz o terminal reconhecer como hyperlink
    console.print(f"\n   🔗 [bold {PALETTE['cyan_bright']}]View on Remote:[/] [link={url}]{url}[/link]")