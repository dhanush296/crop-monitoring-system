from flask import Flask
from flask_cors import CORS
from routes.predict import predict_bp
import os

app = Flask(__name__)
# This is the magic line that fixes 90% of connection issues
CORS(app) 

# Ensure uploads folder exists
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Register the predict route
app.register_blueprint(predict_bp)

@app.route("/")
def home():
    return {"message": "Crop Monitoring Backend is Live"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)