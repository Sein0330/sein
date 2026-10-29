import os
import shutil
import glob

# Folder Download Windows
DOWNLOAD_DIR = "/mnt/c/Users/almaarij/Downloads"
# Folder Tujuan WSL
TARGET_DIR = "/home/almaarij/sein/Bahan Analisa HTML"

# Cari semua file HTML hasil scrape (yang namanya ada angka di depan)
files = glob.glob(f"{DOWNLOAD_DIR}/*.html")

if not files:
    print("❌ Gak ada file HTML di Downloads. Jalanin script DevTools dulu di Chrome.")
    exit()

print(f"✅ Ketemu {len(files)} file HTML. Mindahin ke folder WSL...")

for f in files:
    filename = os.path.basename(f)
    # Cek apakah nama filenya sesuai format (misal: 01_Data_Entry.html)
    if filename[0].isdigit():
        target_path = os.path.join(TARGET_DIR, filename)
        shutil.move(f, target_path)
        print(f"   ✅ Dipindah: {filename}")

print(f"\n🎉 Selesai! Cek folder: {TARGET_DIR}")
