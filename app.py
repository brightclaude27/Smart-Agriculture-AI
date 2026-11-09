import os
import requests
import pandas as pd
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
        # X ni inkingi zose uretse iya nyuma; y ni inkingi ya nyuma (igihingwa)
        X = df.iloc[:, :-1]
        y = df.iloc[:, -1]

        if X.shape[1] != 7:
            print(f"⚠️ Icyitonderwa: CSV yawe ifite inkingi {X.shape[1]} z'ibipimo aho kuba 7.")

        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        print(f"✅ AI Model yigishijwe neza! Inkingi zakoreshejwe: {list(X.columns)}")
        return model, list(X.columns)
    except Exception as e:
        print(f"⚠️ Ikibazo mu gusoma ubutaka_data.csv: {e}")
        return None, []


ai_model, feature_columns = tegura_model()


# =====================================================================
# 2. API YA 1: OPEN-METEO (Endpoint nyayo - Ntisaba API Key)
# =====================================================================
def fata_ikirere_open_meteo(lat, lon):
    try:
        base_url = "https://open-meteo.com"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,rain"
        }
        res = requests.get(base_url, params=params, timeout=8)
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
# 3. API YA 2: OPENWEATHERMAP (Endpoint nyayo - Backup API)
# =====================================================================
def fata_ikirere_openweather(lat, lon):
    if OPENWEATHER_API_KEY == "SHYIRAMO_API_KEY_YAWE_HANO":
        return None
    try:
        base_url = "https://openweathermap.org"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"
        }
        res = requests.get(base_url, params=params, timeout=8)
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
# 4. API YA 3: ISRIC SOILGRIDS REST API (Endpoint nyayo y'Ubutaka)
# =====================================================================
def fata_ubutaka_soilgrids(lat, lon):
    try:
        base_url = "https://isric.org"
        params = {
            "lon": lon,
            "lat": lat,
            "property": ["phh2o", "nitrogen"],
            "depth": "0-5cm",
            "value": "mean"
        }
        res = requests.get(base_url, params=params, timeout=10)
        if res.status_code == 200:
            layers = res.json().get('properties', {}).get('layers', [])
            ph_val = 6.2
            n_val = 50.0

            for layer in layers:
                if layer['name'] == 'phh2o':
                    raw_ph = layer['depths'][0]['values'].get('mean')
                    if raw_ph is not None:
                        ph_val = round(raw_ph / 10.0, 2)
                elif layer['name'] == 'nitrogen':
                    raw_n = layer['depths'][0]['values'].get('mean')
                    if raw_n is not None:
                        n_val = round(raw_n / 100.0, 2)

            return {
                'source': 'ISRIC SoilGrids REST API',
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
        "inkingi_za_model": feature_columns,
        "message": "API irakora neza! Ohereza POST request kuri /api/predict"
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        amakuru = request.get_json() or {}

        # Coordinates z'ifatizo (Nyamagabe, Rwanda) niba umuhinzi atazitanze
        lat = float(amakuru.get('latitude', -2.48))
        lon = float(amakuru.get('longitude', 29.56))

        # A. Gukura amakuru y'ikirere kuri API 1 cyangwa API 2
        ikirere = fata_ikirere_open_meteo(lat, lon) or fata_ikirere_openweather(lat, lon)
        if not ikirere:
            ikirere = {'source': 'Fallback Climate', 'temperature': 21.5, 'humidity': 75.0, 'rainfall': 110.0}

        # B. Gukura amakuru y'ubutaka kuri API 3 (SoilGrids)
        ubutaka = fata_ubutaka_soilgrids(lat, lon)

        # C. Guhuza ibipimo bya API n'ibyo umuhinzi yatanze
        N = float(amakuru.get('N', ubutaka['N']))
        P = float(amakuru.get('P', 45.0))
        K = float(amakuru.get('K', 40.0))
        ph = float(amakuru.get('ph', ubutaka['ph']))
        temp = float(amakuru.get('temperature', ikirere['temperature']))
        hum = float(amakuru.get('humidity', ikirere['humidity']))
        rain = float(amakuru.get('rainfall', ikirere['rainfall']))

        # D. Gukoresha DataFrame ifite amazina y'inkingi (feature_columns) nk'uko CSV imeze
        if ai_model is not None and len(feature_columns) == 7:
            ibipimo_df = pd.DataFrame(
                [[N, P, K, temp, hum, ph, rain]],
                columns=feature_columns
            )
            igihingwa = ai_model.predict(ibipimo_df)[0]
        else:
            igihingwa = "Ibigori cyangwa Ibishyimbo (Reba ko CSV ifite inkingi 7 z'ibipimo)"

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
