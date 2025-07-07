from flask import Flask, render_template, request
import joblib
import numpy as np
import os

app = Flask(__name__)

# Model and scaler paths
MODEL_PATH = "artifacts/models/model.pkl"
SCALER_PATH = "artifacts/processed/scaler.pkl"

# Load model and scaler with error handling
try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully")
    else:
        print(f"Model file not found at {MODEL_PATH}")
        model = None
        
    if os.path.exists(SCALER_PATH):
        scaler = joblib.load(SCALER_PATH)
        print("Scaler loaded successfully")
    else:
        print(f"Scaler file not found at {SCALER_PATH}")
        scaler = None
except Exception as e:
    print(f"Error loading model/scaler: {e}")
    model = None
    scaler = None

# Feature names - make sure these match your training data
FEATURES = [
    'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
    'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
    'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
    'Predictive_Maintenance_Score', 'Error_Rate_%',
    'Year', 'Month', 'Day', 'Hour'
]

# Label mapping
LABELS = {
    0: "Low",
    1: "Medium",
    2: "High"
}

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    
    if request.method == 'POST':
        try:
            # Check if model and scaler are loaded
            if model is None or scaler is None:
                prediction = "Error: Model or scaler not loaded properly"
            else:
                # Extract input data from form
                input_data = []
                for feature in FEATURES:
                    value = request.form.get(feature)
                    if value is None or value == '':
                        raise ValueError(f"Missing value for {feature}")
                    input_data.append(float(value))
                
                # Prepare data for prediction
                input_array = np.array(input_data).reshape(1, -1)
                
                # Scale the input data
                scaled_array = scaler.transform(input_array)
                
                # Make prediction
                pred = model.predict(scaled_array)[0]
                prediction = LABELS.get(pred, "Invalid prediction")
                
        except ValueError as ve:
            prediction = f"Error: Invalid input - {str(ve)}"
        except Exception as e:
            prediction = f"Error: {str(e)}"
    
    return render_template('index.html', prediction=prediction, features=FEATURES)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    status = {
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'status': 'healthy' if (model is not None and scaler is not None) else 'unhealthy'
    }
    return status

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)