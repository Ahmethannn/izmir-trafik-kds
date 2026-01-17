import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from streamlit_folium import st_folium
import time
import plotly.express as px
import plotly.graph_objects as go
import config
import utils

st.set_page_config(page_title="İzmir Trafik Merkezi", layout="wide", page_icon="🚔", initial_sidebar_state="expanded")

with open('style.css') as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'simulasyon_aktif' not in st.session_state: st.session_state['simulasyon_aktif'] = False
if 'su_anki_saat' not in st.session_state: st.session_state['su_anki_saat'] = 6 

def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center;'>🏙️ İBB Trafik</h1>", unsafe_allow_html=True)
        st.markdown("---")
        username = st.text_input("Kullanıcı Adı")
        password = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap", type="primary"):
            if username == "admin" and password == "admin":
                st.session_state['logged_in'] = True; st.rerun()
            else: st.error("❌ Hatalı Giriş")

def main_dashboard():
    df_raw = utils.veriyi_cek()
    if df_raw is None: st.error("Veritabanı hatası! XAMPP MySQL açık mı?"); st.stop()

    if st.session_state['simulasyon_aktif']:
        gosterilecek_saat = st.session_state['su_anki_saat']
        if gosterilecek_saat >= 24:
            st.session_state['simulasyon_aktif'] = False
            st.session_state['su_anki_saat'] = 6
            st.rerun()
    else:
        gosterilecek_saat = 12 

    with st.sidebar:
        st.title("🏙️ İBB ULAŞIM")
        st.success("🟢 Sunucu Online")
        st.markdown("---")
        
        senaryo = st.selectbox("🌪️ Senaryo Modu:", ["Normal Akış", "💥 Kaza: Altınyol", "🚧 Çalışma: Sahil", "⛈️ Yağış"])
        st.markdown("---")
        
        mevcut_gunler = list(df_raw['Gun_Ismi'].unique())
        istenen_default = ['Pazartesi', 'Cuma']
        gecerli_default = [g for g in istenen_default if g in mevcut_gunler]
        if not gecerli_default and mevcut_gunler: gecerli_default = [mevcut_gunler[0]]
        
        disable_filters = st.session_state['simulasyon_aktif']
        secilen_gunler = st.multiselect("📅 Günler", mevcut_gunler, default=gecerli_default, disabled=disable_filters)
        
        if not st.session_state['simulasyon_aktif']:
            kullanici_saati = st.slider("🕒 Saat Seçimi", 0, 23, 18)
            gosterilecek_saat = kullanici_saati 
        else:
             st.info(f"⏳ Simülasyon: Saat {gosterilecek_saat}:00")
             st.progress((gosterilecek_saat - 6) / 18)

        st.markdown("---")
        st.subheader("🎮 Kontrol Paneli")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if not st.session_state['simulasyon_aktif']:
                if st.button("▶️ OYNAT", type="primary"):
                    st.session_state['simulasyon_aktif'] = True
                    st.session_state['su_anki_saat'] = 6 
                    st.rerun()
        with col_b2:
            if st.session_state['simulasyon_aktif']:
                if st.button("⏹️ DURDUR", type="secondary"):
                    st.session_state['simulasyon_aktif'] = False
                    st.rerun()

        st.markdown("---")
        if st.button("🛑 Çıkış"): st.session_state['logged_in'] = False; st.rerun()

    df = df_raw.copy()
    msg = ""
    if senaryo == "💥 Kaza: Altınyol":
        df.loc[df['Cadde'].str.contains("Altınyol"), 'Yogunluk'] = 98
        msg = "💥 ALTINYOL'DA KAZA!"
    elif senaryo == "🚧 Çalışma: Sahil":
        df.loc[df['Cadde'].str.contains("Sahil"), 'Yogunluk'] = 0
        msg = "🚧 SAHİL KAPALI"
    elif senaryo == "⛈️ Yağış":
        df['Yogunluk'] += 20
        msg = "⛈️ YAĞIŞ VAR"
    
    df['Yogunluk'] = df['Yogunluk'].clip(upper=100)

    st.title("🚦 Akıllı Trafik Yönetim Sistemi")
    if msg: st.warning(msg)

    current_df = df[(df['Saat'] == gosterilecek_saat) & (df['Gun_Ismi'].isin(secilen_gunler))]
    ort, en_yogun, durum = utils.kpi_hesapla(current_df)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Şu Anki Saat", f"{gosterilecek_saat}:00")
    kpi2.metric("Ortalama Yoğunluk", f"%{int(ort)}")
    kpi3.metric("Trafik Durumu", durum, delta_color="inverse" if ort>50 else "normal")
    kpi4.metric("Riskli Bölge", en_yogun)

    m = utils.harita_olustur(current_df)
    st_folium(m, width=1400, height=500, key=f"map_{gosterilecek_saat}")

    st.markdown("---")
    st.subheader("📊 Karar Destek Analiz Paneli")
    
    t1, t2, t3, t4, t5 = st.tabs(["🔥 Isı Matrisi", "📦 Risk Analizi", "🏔️ Kümülatif Yük", "🌞 Dağılım", "⚡ Hız Paneli"])
    
    with t1:
        pivot = df.pivot_table(index="Gun_Ismi", columns="Saat", values="Yogunluk", aggfunc="mean")
        st.plotly_chart(px.imshow(pivot, color_continuous_scale="RdYlGn_r", aspect="auto"), use_container_width=True)
        
    with t2:
        st.plotly_chart(utils.grafik_box_plot(df), use_container_width=True)
        
    with t3:
        st.plotly_chart(utils.grafik_area_chart(df), use_container_width=True)
        
    with t4:
        st.plotly_chart(utils.grafik_sunburst(df), use_container_width=True)
        
    with t5:
        c_a, c_b = st.columns(2)
        with c_a: st.plotly_chart(utils.grafik_gauge(ort), use_container_width=True)
        with c_b: 
            bar_data = df.groupby("Cadde")["Yogunluk"].mean().sort_values(ascending=False).reset_index()
            st.plotly_chart(px.bar(bar_data, x="Yogunluk", y="Cadde", orientation='h', color="Yogunluk", color_continuous_scale="Reds"), use_container_width=True)

    if st.session_state['simulasyon_aktif']:
        time.sleep(1) 
        st.session_state['su_anki_saat'] += 1 
        st.rerun() 

if st.session_state['logged_in']:
    main_dashboard()
else:
    login_page()