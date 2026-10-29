import time
import os
import shutil
import glob

DOWNLOAD_DIR = "/mnt/d/upworker html"
TARGET_DIR = "/home/almaarij/sein/Bahan Analisa HTML"

os.makedirs(TARGET_DIR, exist_ok=True)

print(f"[*] Memantau folder: {DOWNLOAD_DIR}")
print(f"[*] Tujuan: {TARGET_DIR}")
print("[*] Mode: Polling (cek tiap 2 detik). Tekan CTRL+C untuk berhenti.\n")

processed_files = set()

try:
    while True:
        # Cari semua file HTML di Downloads
        files = glob.glob(f"{DOWNLOAD_DIR}/*.html")
        
        for f in files:
            filename = os.path.basename(f)
            
            # Cek apakah file ini udah pernah diproses
            if filename in processed_files:
                continue
                
            # Cek apakah ini file hasil scrape (ada angka di depan, misal "01_...")
            if filename[0].isdigit():
                # Kasih jeda 1 detik biar download selesai (file gak ke-lock)
                time.sleep(1)
                
                try:
                    target_path = os.path.join(TARGET_DIR, filename)
                    shutil.move(f, target_path)
                    print(f"[+] Dipindah: {filename}")
                    processed_files.add(filename)
                except Exception as e:
                    print(f"[!] Gagal mindahin {filename}: {e}")
        
        time.sleep(2) # Cek tiap 2 detik

except KeyboardInterrupt:
    print("\n[!] Berhenti memantau.")
