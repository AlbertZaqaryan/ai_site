import pickle
from urllib.request import urlopen
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
# Enable CORS so frontend (running on any port) can call this API
CORS(app)

# Feature names matching the trained model's training dataframe
FEATURE_NAMES = [
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "smoking_history",
    "bmi",
    "HbA1c_level",
    "blood_glucose_level"
]

MODEL_URL = "https://s3.eu-central-1.amazonaws.com/ai.model.bucket/model.pkl"
model = None

def load_model():
    """Loads the model from AWS S3 or fallback to a local pickle file."""
    global model
    try:
        print(f"Downloading model from {MODEL_URL}...")
        with urlopen(MODEL_URL) as response:
            model = pickle.load(response)
        print("Model loaded successfully from S3!")
    except Exception as e:
        print(f"Could not load from URL ({e}). Attempting to load local 'model.pkl'...")
        try:
            with open("model.pkl", "rb") as f:
                model = pickle.load(f)
            print("Loaded local model.pkl successfully!")
        except Exception as local_err:
            print(f"Fatal error: Unable to load model: {local_err}")
            model = None

# Preload model on startup
load_model()

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "online",
        "model_loaded": model is not None
    }), 200

@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model is not loaded on the server."}), 500

    try:
        payload = request.get_json(force=True)

        # Extract features from request body
        features = [
            int(payload.get("gender", 0)),
            float(payload.get("age", 0)),
            int(payload.get("hypertension", 0)),
            int(payload.get("heart_disease", 0)),
            int(payload.get("smoking_history", 0)),
            float(payload.get("bmi", 0)),
            float(payload.get("HbA1c_level", 0)),
            float(payload.get("blood_glucose_level", 0))
        ]

        # Use DataFrame with feature names to fix sklearn's UserWarning
        input_df = pd.DataFrame([features], columns=FEATURE_NAMES)

        # Predict outcome (0: Negative, 1: Positive)
        prediction = model.predict(input_df)[0]

        # Predict probability if model supports it
        probabilities = None
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(input_df)[0].tolist()
            probabilities = {
                "negative": round(probs[0] * 100, 2),
                "positive": round(probs[1] * 100, 2)
            }

        return jsonify({
            "status": "success",
            "prediction": int(prediction),
            "label": "Diabetic" if int(prediction) == 1 else "Non-Diabetic",
            "probabilities": probabilities,
            "received_input": payload
        }), 200

    except Exception as err:
        return jsonify({"error": str(err)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)