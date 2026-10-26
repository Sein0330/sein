#!/bin/bash
# Pastikan lu isi MAXMIND_ACCOUNT_ID & MAXMIND_LICENSE_KEY di .env
source ~/sein/.env

if [ -z "$MAXMIND_ACCOUNT_ID" ] || [ -z "$MAXMIND_LICENSE_KEY" ]; then
    echo "❌ Error: Isi MAXMIND_ACCOUNT_ID dan MAXMIND_LICENSE_KEY di .env dulu bre!"
    exit 1
fi

echo "⏳ Downloading GeoLite2-City database..."
URL="https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=${MAXMIND_LICENSE_KEY}&suffix=tar.gz"
wget -q --show-progress -O /tmp/GeoLite2-City.tar.gz "$URL"

if [ $? -ne 0 ]; then echo "❌ Download gagal. Cek License Key lu."; exit 1; fi

echo "📦 Extracting..."
tar -xzf /tmp/GeoLite2-City.tar.gz -C /tmp/
# Cari file .mmdb di dalam folder hasil extract, copy ke data/
find /tmp -name "GeoLite2-City.mmdb" -exec cp {} ~/sein/data/GeoLite2-City.mmdb \;
rm -rf /tmp/GeoLite2-City.tar.gz /tmp/GeoLite2-City_*

echo "✅ Database berhasil disimpan di data/GeoLite2-City.mmdb"
