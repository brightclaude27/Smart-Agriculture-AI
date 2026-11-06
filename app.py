from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd

# Guhagurutsa FastAPI application
app = FastAPI(
    title="Smart Agriculture AI API",
    description="API ihuza amakuru y'ubutaka n'ubwonko bwa AI ku bwayo",
    version="1.0.0"
)

# 1. Gutegura imiterere y'amakuru API yawe izajya ihabwa (Data Structure)
# Ibi bituma API idashobora kwakira amakuru mabi cyangwa amakuru atuzuye
class UbutakaData(BaseModel):
    temperature: float     # Ubushyuhe
    humidity: float        # Ubuhehere
    ph_level: float        # Urwego rwa aside (pH)
    nitrogen: float        # Nitrogen (N)
    phosphorus: float      # Phosphorus (P)
    potassium: float       # Potassium (K)

# 2. Urubuga rwa mbere (Home Endpoint) kuko iyo umuntu funguye API ari rwo abona
@app.get("/")
def home():
    return {
        "status": "Online",
        "message": "Ikaze kuri Smart Agriculture AI API! Umushinga uri gukora neza.",
        "docs_url": "/docs"  # Hano niho uzasanga urubuga rwo kuyipima (Swagger UI)
    }

# 3. Endpoint ihuza AI n'amakuru y'ubutaka (Prediction Endpoint)
@app.post("/predict-yield/")
def predict_crop_yield(data: UbutakaData):
    # Guhindura amakuru yakiriwe mo DataFrame kugira ngo AI Model (nka Scikit-Learn) ishobore kuyasoma
    input_data = pd.DataFrame([data.dict()])
    
    # HANO NIHO MODEL YAWE IZAKORERA PREDICTION NYACYO NYUMA YO KUYILOADINGA
    # Urugero rw'umwanzuro w'agateganyo (Logic) mu gihe utarahagurutsa model ya .pkl cyangwa .h5
    if data.ph_level < 5.5:
        recommendation = "Ubutaka bufite aside (acid) nyinshi. Inama: Shyiramo ishwagara mu murima."
    elif data.nitrogen < 20:
        recommendation = "Urwego rwa Nitrogen ruri hasi cyane. Inama: Shira mu murima ifumbire ikize kuri NPK."
    elif data.humidity < 40 and data.temperature > 30:
        recommendation = "Ubutaka bwumye kandi harashyushye. Inama: Akora sisitemu yo kwihura (Irrigation system)."
    else:
        recommendation = "Amakuru y'ubutaka meze neza cyane! Bukwiriye guhingwamo ibirayi, ibigori cyangwa ibishyimbo."
        
    return {
        "status": "success",
        "data_received": data.dict(),
        "ai_recommendation": recommendation
    }
