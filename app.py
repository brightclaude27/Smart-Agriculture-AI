import streamlit as st

# 1. SHYIRA AYA MAKURU MASHYA HANO HEJURU (Hasi ya import streamlit)
amakuru_y_ibihingwa = {
    "ibigori": {
        "izina": "Ibigori (Maize)",
        "ph": "5.5 - 7.0",
        "ifumbire": "Nitrogen mwinshi (N) nka Urea/DAP, Phosphorus ngerere.",
        "inama": "Bikunda ubutaka buhehereye neza buva amazi. Shira imvaho ku gipimo cya N: 100 n'ifumbire y'imborera ihagije mu gutera."
    },
    "ibishyimbo": {
        "izina": "Ibishyimbo (Beans)",
        "ph": "6.0 - 7.5",
        "ifumbire": "Phosphorus mwinshi (P) nka DAP mu gutangira. Ntibikunda Nitrogen nywinshi.",
        "inama": "Ibishyimbo bishobora gukora Nitrogen yabyo mu butaka (Nitrogen fixation). Bikunda ubutaka butari aside cyane kandi buva amazi."
    },
    # ... (Shyiramo n'ibindi bihingwa byose kugeza kuri marakuja)
}

st.title("Smart Agriculture AI Search & Predict Engine")
st.write("Urakaza neza! Koresha uru rubuga mu gushakisha no guhanura ibihingwa bikwiriye ubutaka bwawe.")

st.header("🔍 1. AI Search Engine (Shakisha Igihingwa)")

# 2. SHYIRA AKA GACE KO GUSHAKISHA HASI Y'ABO
izina_ryanditswe = st.text_input("Tapamo izina ry'igihingwa (Urugero: Ibigori, Ibishyimbo):").lower().strip()

if izina_ryanditswe in amakuru_y_ibihingwa:
    crop = amakuru_y_ibihingwa[izina_ryanditswe]
    st.success(f"🔍 **Amakuru kuri {crop['izina']}:**")
    st.write(f"• **pH y'Ubutaka ikwiriye:** {crop['ph']}")
    st.write(f"• **Ifumbire ikenewe:** {crop['ifumbire']}")
    st.write(f"• **Inama z'ubuhinzi:** {crop['inama']}")
elif izina_ryanditswe:
    st.warning("Nta makuru ahagije ahari kuri iki gihingwa muri aka kanya.")
