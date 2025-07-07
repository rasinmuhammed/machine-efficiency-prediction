from src.data_processing import DataProcessing
from src.model_training import ModelTraining

if __name__ == "__main__":
    processor = DataProcessing("artifacts/raw/data.csv", "artifacts/processed")
    processor.run()

    model_trainer = ModelTraining("artifacts/processed/", "artifacts/models/")
    model_trainer.run()