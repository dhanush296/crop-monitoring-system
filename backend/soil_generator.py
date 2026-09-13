# soil_simulator.py
from flask import Flask, jsonify
import random

app = Flask(__name__)

@app.route('/api/soil', methods=['GET'])
def get_soil_data():
    # Simulating the physical soil probe
    soil_data = {
        "nitrogen_mg_kg": random.randint(20, 120),
        "phosphorus_mg_kg": random.randint(10, 80),
        "potassium_mg_kg": random.randint(10, 80),
        "moisture_percent": random.randint(10, 90), 
        "ph_level": round(random.uniform(5.5, 7.5), 2)
    }
    return jsonify(soil_data)

if __name__ == '__main__':
    # Runs the simulated sensor on local port 5001
    app.run(port=5001, debug=True)