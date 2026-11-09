import os
import requests
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)
CORS(app)

# Shyiramo API Key yawe ya OpenWeatherMap niba uyifite (cyangwa uyirekere uko iri)
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "SHYIRAMO_API_KEY_YAWE_HANO")

# =====================================================================
# 1. KWIGISHA AI MODEL UKORESHEJE ubutaka_data.csv
# =====================================================================
def tegura_model():
    try:
        df = pd.read_csv('ubutaka_data.csv')
        # Hindura amazina y'inkingi (columns) niba muri CSV yawe atandukanye n'aya
        # Urugero: ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall', 'label']
        X = df.iloc[:, :-1]  # Inkingi zose zibanza (ibipimo)
        y = df.iloc[:, -1]   # Inkingi ya nyuma (izina ry'igihingwa)
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        print("✅ AI Model yigishijwe neza ikoresheje ubutaka_data.csv!")
        return model, list(X.columns)
    except Exception as e:
        print(f"⚠️ Ikibazo mu gusoma ubutaka_data.csv: {e}")
        return None, []

ai_model, feature_columns = tegura_model()


# =====================================================================
# 2. API YA 1: OPEN-METEO (Amakuru y'Ikirere - Ntisaba API Key)
# =====================================================================
def fata_ikirere_open_meteo(lat, lon):
    try:
        url = (
            f"https://open-meteo.com?"
            f"latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,rain"
        )
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            current = res.json().get('current', {})
            return {
                'source': 'Open-Meteo API',
                'temperature': current.get('temperature_2m', 22.0),
                'humidity': current.get('relative_humidity_2m', 70.0),
                'rainfall': current.get('rain', 100.0)
            }
    except Exception as e:
        print(f"Open-Meteo Error: {e}")
    return None


# =====================================================================
# 3. API YA 2: OPENWEATHERMAP (Umufasha w'Ikirere / Backup API)
# =====================================================================
def fata_ikirere_openweather(lat, lon):
    if OPENWEATHER_API_KEY == "SHYIRAMO_API_KEY_YAWE_HANO":
        return None
    try:
        url = (
            f"https://openweathermap.org?"
            f"lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
        )
        res = requests.get(url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            imvura = data.get('rain', {}).get('1h', 80.0)
            return {
                'source': 'OpenWeatherMap API',
                'temperature': data['main']['temp'],
                'humidity': data['main']['humidity'],
                'rainfall': imvura
            }
    except Exception as e:
        print(f"OpenWeather Error: {e}")
    return None


# =====================================================================
# 4. API YA 3: ISRIC SOILGRIDS (Amakuru y'Ubutaka nka pH na Nitrogen)
# =====================================================================
def fata_ubutaka_soilgrids(lat, lon):
    try:
        url = (
            f"https://isric.org?"
            f"lon={lon}&lat={lat}&property=phh2o&property=nitrogen&depth=0-5cm&value=mean"
        )
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            layers = res.json().get('properties', {}).get('layers', [])
            ph_val = 6.2     # Agaciro k'ifatizo niba katabonetse
            n_val = 50.0     # Agaciro k'ifatizo ka Nitrogen
            
            for layer in layers:
                if layer['name'] == 'phh2o':
                    raw_ph = layer['depths'][0]['values'].get('mean')
                    if raw_ph:
                        ph_val = round(raw_ph / 10.0, 2)  # SoilGrids itanga pH yikubye 10
                elif layer['name'] == 'nitrogen':
                    raw_n = layer['depths'][0]['values'].get('mean')
                    if raw_n:
                        n_val = round(raw_n / 100.0, 2)
                        
            return {
                'source': 'ISRIC SoilGrids API',
                'ph': ph_val,
                'N': n_val
            }
    except Exception as e:
        print(f"SoilGrids Error: {e}")
    return {'source': 'Default Values', 'ph': 6.0, 'N': 50.0}


# =====================================================================
# 5. INZIRA YA API (ENDPOINT) IHUZA BYOSE IGAHANURA IGIHINGWA
# =====================================================================
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "online",
        "project": "Smart Agriculture AI",
        "message": "API irakora neza! Ohereza POST request kuri /api/predict"
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        amakuru = request.get_json() or {}
        
        # Urugero rwa Coordinates (Niba umuhinzi atazitanze, hafatwa iza Nyamagabe, Rwanda)
        lat = float(amakuru.get('latitude', -2.48))
        lon = float(amakuru.get('longitude', 29.56))
        
        # A. Gukura amakuru y'ikirere kuri API 1 (Open-Meteo) cyangwa API 2 (OpenWeather)
        ikirere = fata_ikirere_open_meteo(lat, lon) or fata_ikirere_openweather(lat, lon)
        if not ikirere:
            ikirere = {'source': 'Fallback Climate', 'temperature': 21.5, 'humidity': 75.0, 'rainfall': 110.0}
            
        # B. Gukura amakuru y'ubutaka kuri API 3 (ISRIC SoilGrids)
        ubutaka = fata_ubutaka_soilgrids(lat, lon)
        
        # C. Guhuza amakuru ya API n'ayo umuhinzi yiyandikiye (niba hari ayo yatanze)
        N = float(amakuru.get('N', ubutaka['N']))
        P = float(amakuru.get('P', 45.0))  # Phosphorus (ishobora gutangwa n'umuhinzi)
        K = float(amakuru.get('K', 40.0))  # Potassium (ishobora gutangwa n'umuhinzi)
        ph = float(amakuru.get('ph', ubutaka['ph']))
        temp = float(amakuru.get('temperature', ikirere['temperature']))
        hum = float(amakuru.get('humidity', ikirere['humidity']))
        rain = float(amakuru.get('rainfall', ikirere['rainfall']))
        
        # D. Gukoresha AI Model mu guhanura igihingwa
        if ai_model is not None:
            ibipimo = np.array([[N, P, K, temp, hum, ph, rain]])
            igihingwa = ai_model.predict(ibipimo)[0]
        else:
            igihingwa = "Ibigori cyangwa Ibishyimbo (Model ntiyabashije gusoma CSV)"

        return jsonify({
            "status": "success",
            "igihingwa_cyiza": str(igihingwa),
            "ubutumwa": f"Hashingiwe ku makuru yizewe y'ikirere n'ubutaka, igihingwa kiberanye n'uyu murima ni: {igihingwa}",
            "ibipimo_byakoreshejwe": {
                "Nitrogen (N)": N,
                "Phosphorus (P)": P,
                "Potassium (K)": K,
                "pH_yubutaka": ph,
                "Ubushyuhe_C": temp,
                "Ubuhehere_%": hum,
                "Imvura_mm": rain
            },
            "amasoko_yamakuru": [ikirere['source'], ubutaka['source']]
        })

    except Exception as e:
        return jsonify({"status": "error", "ubutumwa": str(e)}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
