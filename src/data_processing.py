import pandas as pd
import numpy as np
import joblib
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class DataProcessing:
    def __init__(self, input_path, output_path):
        self.input_path = input_path
        self.output_path = output_path
        self.df = None
        self.features = None

        os.makedirs(self.output_path, exist_ok=True)
        logger.info("Data Processing initialized.")

    def load_data(self):
        try:
            self.df = pd.read_csv(self.input_path)
            logger.info(f"Data loaded successfully from {self.input_path}")
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException(f"Error loading data: {e}")
        
    def preprocess_data(self):
        try:
            if self.df is None:
                raise CustomException("DataFrame is not loaded. Call load_data() first.")

            self.df["Timestamp"] = pd.to_datetime(self.df["Timestamp"], errors='coerce')

            # Encode categorical features
            categorical_columns = ['Operation_Mode', 'Efficiency_Status']
            for col in categorical_columns:
                self.df[col] = self.df[col].astype('category')

            self.df["Year"] = self.df["Timestamp"].dt.year
            self.df["Month"] = self.df["Timestamp"].dt.month
            self.df["Day"] = self.df["Timestamp"].dt.day

            self.df["Hour"] = self.df["Timestamp"].dt.hour

            self.df.drop(columns=["Timestamp", "Machine_ID"], inplace=True, errors='ignore')

            # Ordinal encoding for Efficiency_Status
            ordered_categories = [["Low", "Medium", "High"]]
            oe = OrdinalEncoder(categories=ordered_categories)
            self.df["Efficiency_Target"] = oe.fit_transform(self.df[["Efficiency_Status"]])

            # Label encoding for Operation_Mode
            le = LabelEncoder()
            self.df["Operation_Mode"] = le.fit_transform(self.df["Operation_Mode"])
            
            logger.info("Data preprocessing completed successfully.")
        except Exception as e:
            logger.error(f"Error during preprocessing: {e}")
            raise CustomException(f"Error during preprocessing: {e}")
        
    def split_and_scale(self):
        try:
            self.features = [
                'Operation_Mode', 'Temperature_C', 'Vibration_Hz',
                'Power_Consumption_kW', 'Network_Latency_ms', 'Packet_Loss_%',
                'Quality_Control_Defect_Rate_%', 'Production_Speed_units_per_hr',
                'Predictive_Maintenance_Score', 'Error_Rate_%', 
                'Year', 'Month', 'Day', 'Hour'
            ]

            X = self.df[self.features]
            y = self.df['Efficiency_Target']

            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

            joblib.dump(X_train, os.path.join(self.output_path, 'X_train.pkl'))
            joblib.dump(X_test, os.path.join(self.output_path, 'X_test.pkl'))
            joblib.dump(y_train, os.path.join(self.output_path, 'y_train.pkl'))
            joblib.dump(y_test, os.path.join(self.output_path, 'y_test.pkl'))
            
            joblib.dump(scaler, os.path.join(self.output_path, 'scaler.pkl'))

            logger.info("Data split and scaling completed successfully.")
        except Exception as e:
            logger.error(f"Error during split and scaling: {e}")
            raise CustomException(f"Error during split and scaling: {e}")
        
    def run(self):
        self.load_data()
        self.preprocess_data()
        self.split_and_scale()
        logger.info("Data processing pipeline completed successfully.")

if __name__ == "__main__":
    processor = DataProcessing("artifacts/raw/data.csv", "artifacts/processed")
    processor.run()


