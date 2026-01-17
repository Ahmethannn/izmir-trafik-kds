import pandas as pd
import folium
from folium.plugins import HeatMap
import plotly.express as px
import plotly.graph_objects as go
import config
import mysql.connector 

def veriyi_cek():
    try:
        conn = mysql.connector.connect(
            host="localhost",      
            user="root",           
            password="",           
            database="izmir_trafik" 
        )
        
        query = "SELECT * FROM trafik_kayitlari"
        df = pd.read_sql(query, conn)
        conn.close()
        
        # Veri Tiplerini Düzelt
        df['Tarih'] = pd.to_datetime(df['Tarih'])
        df['Gun'] = pd.to_numeric(df['Gun'], errors='coerce').fillna(0).astype(int)
        df['Saat'] = pd.to_numeric(df['Saat'], errors='coerce').fillna(0).astype(int)
        df['Enlem'] = pd.to_numeric(df['Enlem'], errors='coerce')
        df['Boylam'] = pd.to_numeric(df['Boylam'], errors='coerce')
        df['Cadde'] = df['Cadde'].str.strip()
        df['Yogunluk'] = pd.to_numeric(df['Yogunluk'], errors='coerce').fillna(0)
        
        gunler = {0:'Pazartesi', 1:'Salı', 2:'Çarşamba', 3:'Perşembe', 4:'Cuma', 5:'Cumartesi', 6:'Pazar'}
        df['Gun_Ismi'] = df['Gun'].map(gunler)
        
        return df
    except Exception as e:
        print(f"MySQL Hatası: {e}")
        return None

def kpi_hesapla(df_local):
    if not df_local.empty:
        ort = df_local["Yogunluk"].mean()
        try:
            en_yogun = df_local.groupby("Cadde")["Yogunluk"].mean().idxmax()
        except:
            en_yogun = "Veri Yok"
            
        if ort > 70: durum = "🚨 KRİTİK"
        elif ort > 45: durum = "⚠️ YOĞUN"
        else: durum = "✅ AKICI"
    else:
        ort = 0; en_yogun = "-"; durum = "-"
    return ort, en_yogun, durum

def harita_olustur(df_local, zoom=12):
    m = folium.Map(location=[38.4237, 27.1428], zoom_start=zoom, tiles="CartoDB dark_matter")
    heatmap_data = []
    
    for cadde_adi, koordinatlar in config.YOL_KOORDINATLARI.items():
        temiz_cadde_adi = cadde_adi.strip()
        cadde_verisi = df_local[df_local["Cadde"] == temiz_cadde_adi]
        
        if not cadde_verisi.empty:
            val = cadde_verisi["Yogunluk"].mean()
        else:
            val = 0
            
        if pd.isna(val): val = 0
        weight = val / 100
        
        for nokta in koordinatlar:
            if val > 0: 
                heatmap_data.append([float(nokta[0]), float(nokta[1]), weight])

    if len(heatmap_data) > 0:
        HeatMap(heatmap_data, radius=25, blur=20, 
                gradient={0.1: 'blue', 0.3: 'lime', 0.6: 'orange', 1: 'red'}).add_to(m)

    return m

# --- GRAFİK FONKSİYONLARI ---

def grafik_sunburst(df):
    ozet = df.groupby(["Gun_Ismi", "Saat"])["Yogunluk"].mean().reset_index()
    fig = px.sunburst(ozet, path=['Gun_Ismi', 'Saat'], values='Yogunluk', title="Zaman Dağılımı", color='Yogunluk', color_continuous_scale='RdYlGn_r')
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    return fig

def grafik_gauge(deger):
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = deger,
        title = {'text': "Ortalama Skor", 'font': {'size': 24, 'color': 'white'}},
        number = {'font': {'size': 50, 'color': 'white'}},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "rgba(255, 255, 255, 0.3)"},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': "white",
            'steps': [
                {'range': [0, 40], 'color': "#00CC96"},
                {'range': [40, 70], 'color': "#FFAA00"},
                {'range': [70, 100], 'color': "#EF553B"}
            ],
            'threshold': {
                'line': {'color': "white", 'width': 4},
                'thickness': 0.75,
                'value': deger
            }
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", 
        font=dict(color="white"), 
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

# --- EKSİK OLAN YENİ GRAFİKLER BURADA ---

def grafik_box_plot(df):
    """Caddelerin Risk/Değişkenlik Analizi (Box Plot)"""
    fig = px.box(df, x="Cadde", y="Yogunluk", color="Cadde", points="outliers", title="Cadde Risk Analizi")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"), showlegend=False)
    return fig

def grafik_area_chart(df):
    """Kümülatif Şehir Yükü (Stacked Area)"""
    gruplanmis = df.groupby(["Saat", "Cadde"])["Yogunluk"].mean().reset_index()
    fig = px.area(gruplanmis, x="Saat", y="Yogunluk", color="Cadde", title="Kümülatif Trafik Yükü")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    return fig