import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# 1. Gutoza AI model mu buryo bwihuse
@st.cache_data
def train_model():
    if not os.path.exists("ubutaka_data.csv"):
        return None
    try:
        df = pd.read_csv("ubutaka_data.csv")
        # Menya neza ko amazina y'inkingi ahura n'ari mu CSV yawe (N, P, K, pH, Temperature, Humidity, Crop)
        X = df[['N', 'P', 'K', 'pH', 'Temperature', 'Humidity']]
        y = df['Crop']
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X.values, y)
        return model
    except Exception as e:
        st.error(f"Hari ikibazo cyabaye mu gutoza AI: {e}")
        return None

model = train_model()

# 2. Gukora urubuga (UI Config)
st.set_page_config(page_title="Smart Agriculture AI", page_icon="🌾", layout="centered")

st.title("🌾 Smart Agriculture AI Search & Predict Engine")
st.write("Urakaza neza! Koresha uru rubuga mu gushakisha no guhanura ibihingwa bikwiriye ubutaka bwawe.")

# GUKORA AGACE K'ISHAKISHA (AI SEARCH ENGINE)
st.markdown("### 🔍 1. AI Search Engine (Shakisha Igihingwa)")
search_query = st.text_input("Tapamo izina ry'igihingwa (Urugero: Ibigori, Ibishyimbo):", "")

if search_query:
    if os.path.exists("ubutaka_data.csv"):
        df = pd.read_csv("ubutaka_data.csv")
        # Gushakisha muri database
        results = df[df['Crop'].str.contains(search_query, case=False, na=False)]
        
        if not results.empty:
            avg_n = results['N'].mean()
            avg_p = results['P'].mean()
            avg_k = results['K'].mean()
            avg_ph = results['pH'].mean()
            
            st.success(f"✅ Amakuru kuri **{search_query}** yabonetse muri AI Knowledge Base!")
            st.info(f"💡 **Inama ya AI:** Igihingwa cya *'{search_query}'* gikura neza mu butaka bufite Nitrogen ya **{avg_n:.1f}**, Phosphorus ya **{avg_p:.1f}**, Potassium ya **{avg_k:.1f}** hamwe na pH ya **{avg_ph:.1f}**.")
        else:
            st.warning(f"❌ Nta makuru ahagije AI ifite kuri '{search_query}' muri ubutaka_data.csv ubu ngubu.")
    else:
        st.error("Dosiye ya ubutaka_data.csv ntabwo iteguye.")

st.markdown("---")

# GUKORA AGACE KO GUHANURA (PREDICTION)
st.markdown("### 🧠 2. Guhanura Igihingwa Cyera (Crop Prediction)")
st.write("Uzuza imiterere y'ubutaka bwawe bwa gihanga:")

col1, col2 = st.columns(2)

with col1:
    n = st.number_input("Nitrogen (N):", min_value=0.0, max_value=200.0, value=50.0)
    p = st.number_input("Phosphorus (P):", min_value=0.0, max_value=200.0, value=50.0)
    k = st.number_input("Potassium (K):", min_value=0.0, max_value=200.0, value=50.0)

with col2:
    ph = st.number_input("pH y'Ubutaka:", min_value=0.0, max_value=14.0, value=6.0)
    temp = st.number_input("Ubushyuhe (Temperature °C):", min_value=0.0, max_value=50.0, value=22.0)
    hum = st.number_input("Ubuhehere (Humidity %):", min_value=0.0, max_value=100.0, value=70.0)

if st.button("Hana Igihingwa Gikwiriye"):
    if model is not None:
        input_data = [[n, p, k, ph, temp, hum]]
        prediction = model.predict(input_data)
        st.balloons()
        st.success(f"🌱 AI iremeza ko igihingwa cyiza cyera hano ari: **{prediction[0]}**")
    else:
