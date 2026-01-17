import pandas as pd
import sqlite3

# 1. CSV Dosyasını Oku
try:
    df = pd.read_csv("izmir_trafik_proje.csv")
    print("CSV dosyası okundu...")
except FileNotFoundError:
    print("HATA: izmir_trafik_proje.csv bulunamadı!")
    exit()

# 2. Veritabanı Bağlantısı Oluştur (Yoksa yaratır)
conn = sqlite3.connect("trafik_veritabani.db")
cursor = conn.cursor()

# 3. Tabloyu SQL formatında kaydet
# Eğer tablo varsa silip yeniden yazar (replace)
df.to_sql("trafik_kayitlari", conn, if_exists="replace", index=False)

print("✅ Başarılı! Veriler 'trafik_veritabani.db' dosyasına SQL tablosu olarak kaydedildi.")
conn.close()