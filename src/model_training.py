import os
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, recall_score, precision_score, f1_score
from src.logger import get_logger
from src.custom_exception import CustomException

logger = get_logger(__name__)

class ModelTraining:
    def __init__(self, processed_data_path, model_output_path):
        self.processed_path = processed_data_path
        self.model_path = model_output_path
        self.clf = None
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None

        os.makedirs(self.model_path, exist_ok=True)
        logger.info("Model Training initialized.")

    def load_data(self):
        try:
            self.X_train = joblib.load(os.path.join(self.processed_path, 'X_train.pkl'))
            self.X_test = joblib.load(os.path.join(self.processed_path, 'X_test.pkl'))
            self.y_train = joblib.load(os.path.join(self.processed_path, 'y_train.pkl'))
            self.y_test = joblib.load(os.path.join(self.processed_path, 'y_test.pkl'))
            logger.info("Data loaded successfully.")

        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise CustomException(f"Error loading data: {e}")
        
    
    def train_model(self):
        try:
            self.clf = LogisticRegression(random_state=42, max_iter=1000)
            self.clf.fit(self.X_train, self.y_train)

            joblib.dump(self.clf, os.path.join(self.model_path, 'model.pkl'))

            logger.info("Model trained and saved successfully.")

        except Exception as e:
            logger.error(f"Error during model training: {e}")
            raise CustomException(f"Error during model training: {e}")

    def evaluate_model(self):
        try:
            y_pred = self.clf.predict(self.X_test)
            
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, average='weighted')
            recall = recall_score(self.y_test, y_pred, average='weighted')
            f1 = f1_score(self.y_test, y_pred, average='weighted')

            logger.info(f"Accuracy: {accuracy:.4f}")
            logger.info(f"Precision: {precision:.4f}")
            logger.info(f"Recall: {recall:.4f}")
            logger.info(f"F1 Score: {f1:.4f}")

            logger.info("Model evaluation completed successfully.")


        except Exception as e:
            logger.error(f"Error during model evaluation: {e}")
            raise CustomException(f"Error during model evaluation: {e}")
        
    def run(self):
        try:
            self.load_data()
            self.train_model()
            self.evaluate_model()
            logger.info("Model training and evaluation completed successfully.")
        except CustomException as ce:
            logger.error(f"Custom Exception: {ce}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise CustomException(f"An unexpected error occurred: {e}")
        
if __name__ == "__main__":
    model_trainer = ModelTraining("artifacts/processed/", "artifacts/models/")
    model_trainer.run()