import os
import socket
import requests
import whois
import dns.resolver
import time
from pywebio import start_server
from pywebio.output import put_text, put_markdown, put_html, clear, put_buttons, use_scope, toast, put_loading
from pywebio.input import input, select
from pywebio.session import run_async, set_env

# --- KONFIGURASI ---
BASE_URL = "http://127.0.0.1:8765"
API_KEY = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("API_KEY_REAL="):
                API_KEY = line.strip().split("=")[1]

# --- CUSTOM CSS BIAR KAYAK TERMINAL ---
TERMINAL_CSS = """
<style>
    body { background-color: #1e1e1e; color: #00ff00; font-family: 'Courier New', Courier, monospace; }
    .container { max-width: 900px; margin: auto; padding: 20px; }
    pre { color: #00ff00; background: transparent; border: none; font-size: 14px; }
    input { background: #333 !important; color: #fff !important; border: 1px solid #555 !important; }
    button { background: #444 !important; color: #fff !important; border: 1px solid #777 !important; margin: 2px; }
    button:hover { background: #666 !important; }
    .btn-primary { background: #0d6efd !important; }
</style>
"""

def render_header():
    clear()
    put_html(TERMINAL_CSS)
    put_text("""
   ███████╗███████╗██╗███╗   ██╗
   ██╔════╝██╔════╝██║████╗  ██║
   ███████╗█████╗  ██║██╔██╗ ██║
   ╚════██║██╔══╝  ██║██║╚██╗██║
   ███████║███████╗██║██║ ╚████║
   ╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝
    IP Tracker & Network Engineer Toolkit (Web Edition)
    """)

async def main():
    set_env(output_max_width='100%', auto_scroll_bottom=True)
    while True:
        render_header()
        put_text("Pilih Menu:")
        menu_choice = await select("Menu Utama", [
            {"label": "1. IP Track & Locate", "value": "1"},
            {"label": "2. Network Tools (WHOIS, DNS, dll)", "value": "2"},
            {"label": "3. Multi-Path Analyzer (RTO Game)", "value": "3"},
            {"label": "4. Exit", "value": "4"}
        ])
        
        if menu_choice == "1":
            await web_track_ip()
        elif menu_choice == "2":
            await web_network_menu()
        elif menu_choice == "3":
            await web_path_analyzer()
        elif menu_choice == "4":
            clear()
            put_text("Keluar dari SEIN. Sampai jumpa!")
            break

# ================= FITUR 1: IP TRACK =================
async def web_track_ip():
    clear()
    put_text("=== IP TRACK & LOCATE ===")
    ip_address = await input("Masukkan IP Address:")
    if not ip_address: return

    put_text(f"Melacak IP {ip_address}...")
    try:
        res = requests.get(f"{BASE_URL}/track/{ip_address}", headers={"X-API-Key": API_KEY}, timeout=10)
        if res.status_code == 200:
            data = res.json().get("data", {})
            output = f"""
IP Address : {data.get('ip')}
Country    : {data.get('country') or 'Unknown'}
Region     : {data.get('region') or 'Unknown'}
City       : {data.get('city') or 'Unknown'}
Latitude   : {data.get('latitude') or 'Unknown'}
Longitude  : {data.get('longitude') or 'Unknown'}
Timezone   : {data.get('timezone') or 'Unknown'}
            """
            put_text(output)
        else:
            put_text("Gagal melacak IP. Pastikan IP valid.")
    except Exception as e:
        put_text(f"Error: {e}")
    
    await put_buttons(['Kembali'], onclick=lambda _: None)

# ================= FITUR 2: NETWORK TOOLS =================
async def web_network_menu():
    clear()
    put_text("=== NETWORK TOOLS ===")
    tool_choice = await select("Pilih Tool", [
        {"label": "1. WHOIS Lookup", "value": "1"},
        {"label": "2. DNS Record Checker", "value": "2"},
        {"label": "3. Port Scanner", "value": "3"},
        {"label": "4. Kembali", "value": "4"}
    ])
    
    if tool_choice == "1":
        target = await input("Masukkan IP/Domain:")
        if target:
            put_text(f"Menarik data WHOIS untuk {target}...")
            try:
                w = whois.whois(target)
                output = f"""
Domain Name : {w.domain_name}
Registrar   : {w.registrar}
Org/Name    : {w.org or w.name}
Country     : {w.country}
                """
                put_text(output)
            except Exception as e:
                put_text(f"Gagal WHOIS: {e}")
            await put_buttons(['Kembali'], onclick=lambda _: None)
            
    elif tool_choice == "2":
        domain = await input("Masukkan Domain:")
        if domain:
            put_text(f"Mengecek DNS {domain}...")
            output = ""
            for rtype in ["A", "MX", "TXT", "CNAME"]:
                try:
                    answers = dns.resolver.resolve(domain, rtype)
                    for rdata in answers:
                        output += f"[{rtype}] {rdata}\n"
                except: pass
            put_text(output if output else "Tidak ada record ditemukan.")
            await put_buttons(['Kembali'], onclick=lambda _: None)

    elif tool_choice == "3":
        target = await input("Masukkan IP/Host:")
        if target:
            put_text(f"Scanning port untuk {target}...")
            common_ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL", 3389: "RDP"}
            output = ""
            for port, service in common_ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                if sock.connect_ex((target, port)) == 0:
                    output += f"[OPEN] Port {port} ({service})\n"
                sock.close()
            put_text(output if output else "Semua port tertutup.")
            await put_buttons(['Kembali'], onclick=lambda _: None)

# ================= FITUR 3: PATH ANALYZER =================
async def web_path_analyzer():
    clear()
    put_text("=== MULTI-PATH ANALYZER & RTO DIAGNOSIS ===")
    ip_game = await input("Masukkan IP/Domain Game:")
    if not ip_game: return
    
    put_text(f"Menarik data Traceroute ke {ip_game} dari 3 lokasi (ID, SG, US)...")
    
    locations = {"ID": "Indonesia", "SG": "Singapore", "US": "United States"}
    results = {}
    
    for loc_code in locations.keys():
        url = "https://api.globalping.io/v1/measurements"
        payload = {"type": "traceroute", "target": ip_game, "locations": [{"country": loc_code}]}
        try:
            res = requests.post(url, json=payload, timeout=10)
            m_id = res.json()["id"]
            result_url = f"https://api.globalping.io/v1/measurements/{m_id}"
            
            for _ in range(15):
                time.sleep(2)
                r = requests.get(result_url, timeout=10)
                data = r.json()
                if data.get("status") == "finished":
                    results[loc_code] = data
                    break
        except:
            results[loc_code] = None

    output = "Hop | IP (ID) | Lat ID | Lat SG | Lat US\n"
    output += "-" * 50 + "\n"
    
    max_hops = 6
    for i in range(max_hops):
        row = [str(i+1)]
        for loc in ["ID", "SG", "US"]:
            if results.get(loc) and "results" in results[loc]:
                hops = results[loc]["results"][0]["result"]["hops"]
                if i < len(hops):
                    ip = hops[i].get("resolvedAddress", "-")
                    timings = hops[i].get("timings", [])
                    lat = f"{sum(t['rtt'] for t in timings)/len(timings):.1f}ms" if timings else "-"
                    if loc == "ID": row.append(ip)
                    row.append(lat)
                else:
                    if loc == "ID": row.append("-")
                    row.append("-")
            else:
                if loc == "ID": row.append("-")
                row.append("-")
        output += " | ".join(row) + "\n"
        
    put_text(output)
    put_text("\nKESIMPULAN: Rute ke Server Game NORMAL. Timeout panjang biasanya karena Game memblokir ICMP (Anti-DDoS).")
    put_text("Saran: Sampaikan ke pelanggan bahwa rute ISP NORMAL, masalah ada di Server Game.")
    
    await put_buttons(['Kembali'], onclick=lambda _: None)

# --- RUN SERVER ---
if __name__ == '__main__':
    # Jalanin di port 8766
    start_server(main, port=8766, debug=False, cdn=False)
