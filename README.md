#  İzmir Kenti Ana Arterleri İçin Simülasyon Tabanlı Akıllı Trafik Karar Destek Sistemi

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-red)
![MySQL](https://img.shields.io/badge/Database-MySQL-orange)
![Status](https://img.shields.io/badge/Status-Completed-green)

Bu proje, İzmir ili ana arterlerindeki trafik yoğunluğunu analiz eden, görselleştiren ve olası kriz senaryolarını (kaza, yol çalışması vb.) simüle ederek yöneticilere stratejik karar alma desteği sunan web tabanlı bir **Karar Destek Sistemidir (KDS)**.

##  Özellikler

- ** Anlık Veri İzleme:** MySQL veritabanından çekilen verilerin canlı görselleştirilmesi.
- ** Canlı Simülasyon:** 06:00 - 24:00 arası trafik akışının "Time-Lapse" (Hızlandırılmış) olarak oynatılması.
- ** What-If (Senaryo) Analizi:**
  - *Kaza Senaryosu:* Belirli bir caddede kaza olduğunda diğer yollara binen yükü hesaplar.
  - *Yol Çalışması:* Bir yol kapatıldığında trafiğin nasıl kilitlendiğini modeller.
- ** Gelişmiş Analitik Grafikler:**
  - **Isı Matrisi (Heatmap):** Yoğun saatlerin analizi.
  - **Risk Analizi (Box Plot):** Caddelerin tıkanıklık risk seviyeleri.
  - **Kümülatif Yük (Area Chart):** Şehrin saatlik toplam trafik stresi.
  - **Hız Kadranı (Gauge):** Anlık şehir trafik skoru.

##  Kullanılan Teknolojiler

* **Dil:** Python 3.12
* **Arayüz:** Streamlit
* **Veritabanı:** MySQL (XAMPP / phpMyAdmin)
* **Veri İşleme:** Pandas, NumPy
* **Görselleştirme:** Folium (Harita), Plotly Express & Graph Objects

##  Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

### 1. Gereksinimlerin Yüklenmesi
Terminal veya komut satırını açarak gerekli kütüphaneleri yükleyin:
```bash
pip install streamlit pandas mysql-connector-python folium streamlit-folium plotly
