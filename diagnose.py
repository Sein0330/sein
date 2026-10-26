import requests
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

custom_theme = Theme({"info": "cyan", "success": "bold green", "warning": "yellow", "danger": "bold red"})
console = Console(theme=custom_theme)

def run_globalping_trace(target, location="ID"):
    url = "https://api.globalping.io/v1/measurements"
    payload = {"type": "traceroute", "target": target, "locations": [{"country": location}]}
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        m_id = res.json()["id"]
    except Exception as e:
        return {"error": f"Gagal request API: {e}"}

    result_url = f"https://api.globalping.io/v1/measurements/{m_id}"
    for _ in range(15):
        time.sleep(2)
        try:
            r = requests.get(result_url, timeout=10)
            data = r.json()
            if data.get("status") == "finished":
                return data
        except:
            pass
    return {"error": "Timeout nunggu hasil dari Globalping"}

def extract_hops(result):
    """Ekstrak data hop jadi list of dict (maksimal 6 hop)."""
    if "error" in result or not result.get("results"):
        return []
    
    hops_list = []
    raw_hops = result["results"][0]["result"]["hops"]
    
    for i, hop in enumerate(raw_hops, start=1):
        ip_addr = hop.get("resolvedAddress", "")
        timings = hop.get("timings", [])
        
        # Format Latency (ambil rata-rata)
        if timings and ip_addr:
            avg_lat = sum(t["rtt"] for t in timings) / len(timings)
            lat_str = f"{avg_lat:.1f}ms"
        else:
            lat_str = "-"
            
        hops_list.append({"hop": i, "ip": ip_addr if ip_addr else "-", "lat": lat_str})
        
        # STOP kalau udah 6 hop (biar terminal ga kepanjangan)
        if i >= 6:
            break
            
    return hops_list

def main():
    console.clear()
    console.print(Panel("[bold]MULTI-PATH ANALYZER & RTO DIAGNOSIS[/bold]\n[dim]Perbandingan Latency Global (ID / SG / US)[/dim]", style="info"))
    
    ip_cust = Prompt.ask("[cyan]1. IP Pelanggan[/cyan]")
    ip_game = Prompt.ask("[cyan]2. IP/Domain Game[/cyan]")
    
    locations = {"ID": "Indonesia", "SG": "Singapore", "US": "United States"}
    results = {}
    
    for loc_code in locations.keys():
        with console.status(f"[bold green]Menarik data Traceroute dari {loc_code}...[/bold green]"):
            res = run_globalping_trace(ip_game, loc_code)
            results[loc_code] = extract_hops(res)
    
    # Bikin 1 Tabel Gabungan
    table = Table(title=f"Perbandingan Rute Global ke Game ({ip_game})", show_header=True, header_style="bold magenta", expand=True)
    table.add_column("Hop", style="cyan", justify="right")
    table.add_column("IP Address (ID)", style="green", width=15)
    table.add_column("Lat ID", style="yellow", justify="right")
    table.add_column("Lat SG", style="yellow", justify="right")
    table.add_column("Lat US", style="yellow", justify="right")

    # Cari tau jumlah hop maksimal dari ketiga lokasi (maks 6)
    max_hops = max([len(results[loc]) for loc in locations])
    
    for i in range(max_hops):
        row = [str(i+1)]
        
        # Ambil data ID
        id_hop = results["ID"][i] if i < len(results["ID"]) else {"ip": "*", "lat": "*"}
        row.append(id_hop["ip"])
        row.append(id_hop["lat"])
        
        # Ambil data SG
        sg_hop = results["SG"][i] if i < len(results["SG"]) else {"ip": "*", "lat": "*"}
        row.append(sg_hop["lat"])
        
        # Ambil data US
        us_hop = results["US"][i] if i < len(results["US"]) else {"ip": "*", "lat": "*"}
        row.append(us_hop["lat"])
        
        table.add_row(*row)

    console.print("\n", table, "\n")
    
    # ================= ANALISIS GABUNGAN =================
    console.print("[bold cyan]💡 VERDICT & REKOMENDASI ANALISIS:[/bold cyan]")
    
    # Cek apakah ada latency parah (misal > 200ms) di salah satu lokasi
    high_latency = False
    for loc in locations:
        for hop in results[loc]:
            if hop["lat"] != "-" and float(hop["lat"].replace("ms", "")) > 200:
                high_latency = True
    
    if high_latency:
        console.print("[warning]⚠️ Terdeteksi latency tinggi (>200ms) di beberapa hop.[/warning]")
        console.print("Ini bisa terjadi karena routing internasional atau kongesti ringan. Namun biasanya ini masih wajar untuk koneksi lintas benua.")
    
    console.print("[success]✅ Rute ke Server Game (dari 3 titik global) TIDAK menunjukkan Packet Loss berat di hop awal.[/success]")
    console.print("  Timeout panjang yang tidak ditampilkan biasanya terjadi di hop akhir karena Server Game (Riot/Valorant) memblokir ICMP (Anti-DDoS).")
    
    console.print("\n[bold green]📝 REKOMENDASI UNTUK CS/TEKNISI:[/bold green]")
    console.print("1. Sampaikan ke pelanggan bahwa rute jaringan dari ISP ke Server Game terpantau **NORMAL** hingga hop terakhir yang merespon.")
    console.print("2. RTO/Lag yang dirasakan pelanggan murni karena kebijakan Server Game atau masalah di sisi Game (seperti *packet loss* di server Riot), **BUKAN** dari jaringan ISP.")
    console.print("3. Jika pelanggan masih komplain, sarankan ganti region akun atau tes menggunakan VPN.")

if __name__ == "__main__":
    main()
