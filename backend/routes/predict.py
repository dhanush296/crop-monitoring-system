from flask import Blueprint, request, jsonify
from PIL import Image
import numpy as np
try:
    import tensorflow as tf
except ImportError:
    tf = None
import os
import random  # Added for dynamic soil simulation
import requests
import json 

predict_bp = Blueprint("predict", __name__)

# Load the REAL AI model and Class Names
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models")
try:
    crop_model = tf.keras.models.load_model(os.path.join(MODEL_DIR, "crop_model_fixed.keras"), compile=False)
    
    with open(os.path.join(MODEL_DIR, "class_names.json"), 'r') as f:
        class_names = json.load(f)
    print("✅ Real AI Brain and Class Names Loaded!")
except Exception as e:
    crop_model = None
    class_names = ["System Error"]
    print(f"⚠️ Warning: Could not load model. {e}")

# Helper 1: Live Weather API (Now Supports BOTH City Names and GPS Coordinates)
def get_weather_and_pest_risk(location_query):
    API_KEY = "971e886fa6aa20830311a1030ccac4fa" 
    
    # 📍 GPS BYPASS LOGIC
    # Clean the string to check if it's just numbers, commas, and negative signs
    clean_check = location_query.replace(",", "").replace(".", "").replace("-", "").replace(" ", "")
    
    if "," in location_query and clean_check.isdigit():
        # User clicked the GPS button! Use the coordinate API endpoint
        lat_str, lon_str = location_query.split(",")
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat_str.strip()}&lon={lon_str.strip()}&appid={API_KEY}&units=metric"
        print(f"📍 Routing via GPS Coordinates: {lat_str}, {lon_str}")
    else:
        # User typed a city name. Use the standard city query endpoint
        url = f"http://api.openweathermap.org/data/2.5/weather?q={location_query}&appid={API_KEY}&units=metric"
        print(f"🏙️ Routing via City Name: {location_query}")

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            lat = data["coord"]["lat"] # Always grabs actual GPS, even if user typed a city!
            lon = data["coord"]["lon"] 

            if humidity > 75 and temp > 25:
                risk = "High"
            elif humidity > 60:
                risk = "Medium"
            else:
                risk = "Low"

            return {"temp": temp, "humidity": humidity, "risk": risk, "lat": lat, "lon": lon}
        else:
            print(f"Weather API Warning: Status Code {response.status_code}")
    except Exception as e:
        print("Weather API error:", e)

    # Fallback default to Bangalore coordinates
    return {"temp": 32, "humidity": 65, "risk": "Medium (Simulated)", "lat": 12.97, "lon": 77.59}

# Helper 2: Synthetic NPK + REAL Live Soil Telemetry + Dynamic Scoring
def get_soil_data(location_name, lat, lon):
    # Base defaults
    soil_info = {"N": 65, "P": 40, "K": 55, "pH": 6.7, "soil_score": 85, "moisture": 42.5, "soil_temp": 24.0} 
    
    # 1. DYNAMIC NPK SIMULATION (Replaces static CSV lookup)
    print(f"🌱 Generating dynamic simulated NPK data for {location_name}...")
    soil_info.update({
        "N": random.randint(30, 100),    # Nitrogen (mg/kg) - adjusted for realistic crop bounds
        "P": random.randint(15, 60),     # Phosphorus (mg/kg)
        "K": random.randint(20, 80),     # Potassium (mg/kg)
        "pH": round(random.uniform(5.5, 7.8), 2), # Soil pH
        "soil_score": 90                 # Starting high score before heuristic penalties
    })

    # 2. Fetch REAL Live Soil Data (Open-Meteo API)
    try:
        meteo_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=soil_temperature_6cm,soil_moisture_3_to_9cm"
        response = requests.get(meteo_url)
        if response.status_code == 200:
            data = response.json()
            if "current" in data:
                soil_info["soil_temp"] = data["current"]["soil_temperature_6cm"]
                soil_moisture_raw = data["current"]["soil_moisture_3_to_9cm"]
                soil_info["moisture"] = round(soil_moisture_raw * 100, 1)
    except Exception as e:
        print(f"Soil API Error: {e}")

    # 3. 🧠 ALGORITHM: Calculate Dynamic Soil Score (Your Heuristic Logic Engine!)
    dynamic_score = soil_info["soil_score"]
    
    # Penalty 1: Extreme Moisture (Ideal is 30% to 60%)
    if soil_info["moisture"] < 25:
        dynamic_score -= 15  # Too dry!
    elif soil_info["moisture"] > 70:
        dynamic_score -= 10  # Too wet!
        
    # Penalty 2: Extreme Soil Temperature (Ideal is 18°C to 30°C)
    if soil_info["soil_temp"] > 32:
        dynamic_score -= 12  # Heat stress!
    elif soil_info["soil_temp"] < 15:
        dynamic_score -= 8   # Too cold!

    # Penalty 3: Low Base Nutrients (N or K dropping too low)
    if soil_info["N"] < 40 or soil_info["K"] < 40:
        dynamic_score -= 10 

    # Ensure the score never drops below 0 or goes above 100
    soil_info["soil_score"] = max(0, min(100, dynamic_score))

    return soil_info

@predict_bp.route("/predict", methods=["POST"])
def predict():
    file = request.files.get("image")
    location = request.form.get("location")

    if not file or not location:
        return jsonify({"error": "Missing image or location"}), 400

    # 1. Image Processing
    img = Image.open(file).resize((224, 224))
    if img.mode != 'RGB':
        img = img.convert('RGB')
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    # 2. REAL Model Prediction (No Confidence Score)
    if crop_model and len(class_names) > 1:
        predictions = crop_model.predict(img_array)
        predicted_index = np.argmax(predictions[0])
        raw_health_name = class_names[predicted_index]
        crop_health = raw_health_name.replace('_', ' ').title()
    else:
        crop_health = "System Error"

    # 3. Fetch Data 
    weather_data = get_weather_and_pest_risk(location)
    soil_data = get_soil_data(location, weather_data["lat"], weather_data["lon"])

    # 4. Return the dynamic payload
    return jsonify({
        "crop_health": crop_health,
        "soil_score": soil_data["soil_score"],
        "npk_values": [soil_data["N"], soil_data["P"], soil_data["K"]],
        "pest_risk": weather_data["risk"],
        "temperature": weather_data["temp"],
        "humidity": weather_data["humidity"],
        "soil_moisture": soil_data["moisture"],  
        "soil_temp": soil_data["soil_temp"]      
    })