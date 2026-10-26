import os
import requests
import sys
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

# Setup tema warna
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "yellow",
    "danger": "bold red",
    "menu": "bold magenta"
})
console = Console(theme=custom_theme)

# Load API Key dari .env
API_KEY = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY_REAL="):
                API_KEY = line.strip().split("=")[1]

BASE_URL = "http://127.0.0.1:8765" # Nembak ke localhost dulu

def show_logo():
    console.clear()
    logo = """
[bold cyan]
   ███████╗███████╗██╗███╗   ██╗
   ██╔════╝██╔════╝██║████╗  ██║
   ███████╗█████╗  ██║██╔██╗ ██║
   ╚════██║██╔══╝  ██║██║╚██╗██║
   ███████║███████╗██║██║ ╚████║
   ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝
[/bold cyan]
[dim]   IP Tracker & Cyber Reconnaissance Tool[/dim]
[dim]   Version 1.0.0 - Made by almaarij[/dim]
    """
    console.print(logo)

def menu():
    while True:
        show_logo()
        console.print("[menu](1)[/menu] IP Track & Locate")
        console.print("[menu](2)[/menu] Lihat Honeypot Logs (Soon)")
        console.print("[menu](3)[/menu] Soon ...")
        console.print("[menu](4)[/menu] Exit\n")
        
        choice = Prompt.ask("[bold yellow]Pilih menu[/bold yellow]", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            track_ip()
        elif choice == "4":
            console.print("[info]Keluar dari SEIN. Sampai jumpa![/info]")
            sys.exit(0)
        else:
            console.print("[warning]Fitur belum tersedia bre![/warning]")
            Prompt.ask("Tekan ENTER untuk kembali")

def track_ip():
    console.clear()
    console.print(Panel("[bold]IP Track & Locate[/bold]\nMasukkan IP Address untuk dilacak.", style="info"))
    
    ip_address = Prompt.ask("Submit IP Address")
    
    if not ip_address:
        return

    with console.status("[bold green]Melacak IP...[/bold green]"):
        try:
            headers = {"X-API-Key": API_KEY}
            res = requests.get(f"{BASE_URL}/track/{ip_address}", headers=headers, timeout=10)
            
            if res.status_code == 200:
                data = res.json().get("data", {})
                
                # Bikin tabel cantik
                table = Table(title=f"Hasil Pelacakan: {ip_address}", show_header=True, header_style="bold magenta")
                table.add_column("Field", style="cyan")
                table.add_column("Value", style="green")
                
                table.add_row("IP Address", str(data.get('ip')))
                table.add_row("Country", str(data.get('country') or "Unknown"))
                table.add_row("Region", str(data.get('region') or "Unknown"))
                table.add_row("City", str(data.get('city') or "Unknown"))
                table.add_row("Latitude", str(data.get('latitude') or "Unknown"))
                table.add_row("Longitude", str(data.get('longitude') or "Unknown"))
                table.add_row("Timezone", str(data.get('timezone') or "Unknown"))
                
                console.print("\n")
                console.print(table)
                console.print("\n")
            elif res.status_code == 401:
                console.print("[danger]Gagal: API Key salah atau tidak valid![/danger]")
            elif res.status_code == 404:
                console.print("[warning]Gagal: IP tidak ditemukan di database.[/warning]")
            else:
                console.print(f"[danger]Error {res.status_code}: {res.text}[/danger]")
                
        except requests.exceptions.ConnectionError:
            console.print("[danger]Gagal terhubung ke server SEIN. Pastiin service nyala![/danger]")
        except Exception as e:
            console.print(f"[danger]Error: {e}[/danger]")
            
    Prompt.ask("\nTekan ENTER untuk kembali ke menu")

if __name__ == "__main__":
    if not API_KEY:
        console.print("[danger]API_KEY_REAL tidak ditemukan di .env![/danger]")
        sys.exit(1)
    menu()
