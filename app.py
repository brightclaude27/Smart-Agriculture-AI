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
        
        # Gukosora amakosa y'inyuguti nkuru n'intoya n'utwanya tw'abasaguye
        df.columns = df.columns.str.strip().str.lower()
        
        # Gufata inkingi 6 za mbere nk'ibiranga ubutaka (Features) n'izina ryose zaba zifite
        X = df.iloc[:, 0:6]
        
        # Gufata inkingi ya 7 nka Crop (Target)
        y = df.iloc[:, 6]
        
        model = RandomForestClassifier(random_state=42)
        model.fit(X.values, y)
        return model, df
    except Exception as e:
        st.error(f"Hari ikibazo cyabaye mu gutoza AI: {e}")
        return None, None

model, df_clean = train_model()

# 2. Gukora urubuga (UI Config)
st.set_page_config(page_title="Smart Agriculture AI", page_icon="🌾", layout="centered")

st.title("🌾 Smart Agriculture AI Search & Predict Engine")
st.write("Urakaza neza! Koresha uru rubuga mu gushakisha no guhanura ibihingwa bikwiriye ubutaka bwawe.")

# GUKORA AGACE K'ISHAKISHA (AI SEARCH ENGINE)
st.markdown("### 🔍 1. AI Search Engine (Shakisha Igihingwa)")
search_query = st.text_input("Tapamo izina ry'igihingwa (Urugero: Ibigori, Ibishyimbo):", "")

if search_query and df_clean is not None:
    # Gushakisha inkingi y'igihingwa (iri ku mwanya wa nyuma)
    crop_col = df_clean.columns[6]
    results = df_clean[df_clean[crop_col].astype(str).str.contains(search_query, case=False, na=False)]
    
    if not results.empty:
        # Gufata imirongo ya mbere y'inkingi z'imibare
        avg_n = results.iloc[:, 0].mean()
        avg_p = results.iloc[:, 1].mean()
        avg_k = results.iloc[:, 2].mean()
        avg_ph = results.iloc[:, 3].mean()
        
        st.success(f"✅ Amakuru kuri **{search_query}** yabonetse muri AI Knowledge Base!")
        st.info(f"💡 **Inama ya AI:** Igihingwa cya *'{search_query}'* gikura neza mu butaka bufite Nitrogen ya **{avg_n:.1f}**, Phosphorus ya **{avg_p:.1f}**, Potassium ya **{avg_k:.1f}** hamwe na pH ya **{avg_ph:.1f}**.")
    else:
        st.warning(f"❌ Nta makuru ahagije AI ifite kuri '{search_query}' muri ubutaka_data.csv ubu ngubu.")

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
        st.error("Model ya AI ntabwo yatojwe neza. Reba niba ubutaka_data.csv irimo amakuru meza.")
