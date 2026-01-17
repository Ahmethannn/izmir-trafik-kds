import sqlite3

print("⏳ Veritabanı dönüştürme işlemi başladı (V4.1)...")

# 1. SQLite Veritabanına Bağlan
try:
    conn = sqlite3.connect("trafik_veritabani.db")
    cursor = conn.cursor()
    
    # Tüm verileri çek
    cursor.execute("SELECT * FROM trafik_kayitlari")
    veriler = cursor.fetchall()
    
    # Sütun isimlerini veritabanından OTOMATİK öğren
    if cursor.description:
        sutun_isimleri = [description[0] for description in cursor.description]
        print(f"📂 Tespit Edilen Sütunlar: {sutun_isimleri}")
        print(f"📊 Toplam Satır: {len(veriler)}")
    else:
        print("❌ Hata: Tabloda sütun bilgisi bulunamadı.")
        exit()
    
    conn.close()
except Exception as e:
    print(f"❌ SQLite Hatası: {e}")
    exit()

# 2. SQL Dosyasını Hazırla
sql_dosya_adi = "phpmyadmin_icin.sql"

def sql_formatla(deger):
    """Veri tipine göre SQL formatına çevirir."""
    if deger is None:
        return "NULL"
    if isinstance(deger, str):
        # Tırnak işaretlerini temizle ve metni tırnak içine al
        temiz = deger.replace("'", "")
        return f"'{temiz}'"
    return str(deger)

try:
    with open(sql_dosya_adi, "w", encoding="utf-8") as f:
        f.write("-- SQLite to MySQL Converter V4.1 (Dynamic)\n")
        f.write("DROP TABLE IF EXISTS trafik_kayitlari;\n\n")
        
        # 3. Tablo Oluşturma Komutunu Dinamik Hazırla
        # Hata olmaması için sütun isimlerini tırnak içine alıyoruz (`isim`)
        # Veri tiplerini güvenli olsun diye TEXT yapıyoruz (MySQL otomatik çevirir)
        sutunlar_sql = ",\n    ".join([f"`{col}` TEXT" for col in sutun_isimleri])
        
        create_query = f"""
CREATE TABLE trafik_kayitlari (
    id INT AUTO_INCREMENT PRIMARY KEY,
    {sutunlar_sql}
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
\n"""
        # HATA BURADAYDI, DÜZELTİLDİ:
        f.write(create_query)
        
        # 4. Verileri Ekleme Komutu (INSERT)
        sutun_adlari_str = ", ".join([f"`{col}`" for col in sutun_isimleri])
        f.write(f"INSERT INTO trafik_kayitlari ({sutun_adlari_str}) VALUES\n")
        
        veriler_sql = []
        for satir in veriler:
            # Satırdaki her bir hücreyi tek tek kontrol edip formatla
            satir_degerleri = [sql_formatla(hucre) for hucre in satir]
            
            # (Deger1, Deger2, ...) haline getir
            satir_str = "(" + ", ".join(satir_degerleri) + ")"
            veriler_sql.append(satir_str)
        
        # Dosyaya yaz
        f.write(",\n".join(veriler_sql))
        f.write(";\n")

    print(f"✅ BAŞARILI! '{sql_dosya_adi}' dosyası hatasız oluşturuldu.")
    print("👉 Şimdi phpMyAdmin'e gidip bu dosyayı yükleyebilirsin.")

except Exception as e:
    print(f"❌ Dosya Yazma Hatası: {e}")