import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import streamlit as st

# 1. Gutoza AI model mu buryo bwihuse
@st.cache_data
def train_model():
    if not os.path.exists("ubutaka_data.csv"):
        return None, None
    try:
        df = pd.read_csv("ubutaka_data.csv")
        
        # Gukosora amakosa y'inyuguti nkuru n'intoya n'utwanya tw'abasaguye
        df.columns = df.columns.str.strip().str.lower()
        
        # Gushakisha inkingi y'igihingwa (crop) ititaye ku buryo yanditse
        crop_col = [col for col in df.columns if 'crop' in col or 'ihingwa' in col]
        if not crop_col:
            # Niba itabonetse, dufata inkingi ya nyuma nka target
            crop_name = df.columns[-1]
        else:
            crop_name = crop_col[0]
            
        # Gufata izindi nkingi zose zisigaye nk'ibiranga ubutaka (Features)
        feature_cols = [col for col in df.columns if col != crop_name]
        
        X = df[feature_cols]
        y = df[crop_name]
        
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
    # Gushakisha inkingi y'igihingwa
    crop_col = [col for col in df_clean.columns if 'crop' in col or 'ihingwa' in col]
    crop_name = crop_col[0] if crop_col else df_clean.columns[-1]
    
    results = df_clean[df_clean[crop_name].astype(str).str.contains(search_query, case=False, na=False)]
    
    if not results.empty:
        # Gushakisha inkingi z'imibare mu buryo bwikora
        num_cols = results.select_dtypes(include=['number']).columns
        
        # Gutanga inama hashingiye ku nkingi zihari
        advice_text = f"✅ Amakuru kuri **{search_query}** yabonetse muri AI Knowledge Base!\n\n💡 **Inama ya AI:** Igihingwa cya *'{search_query}'* gikura neza mu butaka bufite iyi miterere:\n"
        for col in num_cols:
            avg_val = results[col].mean()
            advice_text += f"- **{col.upper()}**: {avg_val:.1f}\n"
            
        st.success(f"✅ Byabonetse!")
        st.info(advice_text)
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
        # Gufata ibipimo 6 by'ibanze biba bikenewe na model
        input_data = [[n, p, k, ph, temp, hum]]
        prediction = model.predict(input_data)
        st.balloons()
        st.success(f"🌱 AI iremeza ko igihingwa cyiza cyera hano ari: **{prediction[0]}**")
    else:
        st.error("Model ya AI ntabwo yatojwe neza. Reba niba ubutaka_data.csv irimo amakuru meza.")
