from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel
from rich.text import Text

# Sua Paleta Cyber Blue
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
    Exibe o banner limpo, em linha única e largura total.
    Sem emojis aqui para garantir estabilidade no Windows.
    """
    
    # Montamos apenas o texto essencial
    banner_text = Text.assemble(
        ("GitScribe ", f"bold {PALETTE['white']}"),
        ("v0.2.0", f"dim {PALETTE['cyan_bright']}")
    )
    
    # Painel Full-Width seguro
    console.print(Panel(
        banner_text,
        style=f"{PALETTE['white']} on {PALETTE['deep_navy']}",
        border_style=PALETTE['blue_vivid'],
        title="[italic]AI-Powered Commit Tool[/italic]",
        title_align="right",
        expand=True,   # Agora é seguro usar expand=True
        padding=(0, 1) # Altura mínima (Linha única)
    ))
    
    # Removemos a linha inferior separada para ficar mais clean,
    # já que o painel já tem borda.

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