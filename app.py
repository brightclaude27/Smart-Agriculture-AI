import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

@st.cache_data
def train_model():
    try:
        df = pd.read_csv("ubutaka_data.csv")
        X = df[['N', 'P', 'K', 'temperature', 'ph']]
        y = df['crop']
        model = RandomForestClassifier(random_state=42)
        model.fit(X.values, y)
        return model
    except Exception as e:
        st.error(f"Hari ikibazo cyabaye mu gutoza AI: {e}")
        return None

model = train_model()

st.set_page_config(page_title="Smart Agriculture AI", page_icon="🌾", layout="centered")
st.title("🌾 AI Igira Inama Abahinzi b'i Rwanda")
st.write("Uzuza imiterere y'ubutaka bwawe hano n'ikirere kugira ngo AI ikubwire igihingwa cyakwera neza.")

st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    n = st.number_input("Urwego rwa Azote (Nitrogen - N):", min_value=0, max_value=150, value=50)
    p = st.number_input("Urwego rwa Fosifore (Phosphorus - P):", min_value=0, max_value=150, value=40)
    k = st.number_input("Urwego rwa Potasiyumu (Potassium - K):", min_value=0, max_value=150, value=40)

with col2:
    temp = st.number_input("Ubushyuhe bw'Akarere (Temperature in °C):", min_value=10.0, max_value=45.0, value=22.0, step=0.5)
    ph = st.number_input("Urwego rwa pH y'ubutaka (Acidic/Alkaline):", min_value=4.0, max_value=9.0, value=6.2, step=0.1)

st.markdown("---")

if st.button("Emeza urebere igihingwa", use_container_width=True):
    if model is not None:
        prediction = model.predict([[n, p, k, temp, ph]])
        st.success(f"🎉 Hashingiwe ku miterere y'ubutaka watanze, igihingwa cyakwera neza cyane ni: **{prediction[0]}**!")
    else:
        st.error("AI ntabwo yiteguye gukora neza kuko ifayili y'amakuru irimo amakosa.")
