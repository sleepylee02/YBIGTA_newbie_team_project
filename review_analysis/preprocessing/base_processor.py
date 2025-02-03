from abc import ABC, abstractmethod
import uuid
import pandas as pd


class BaseDataProcessor:
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
    
    def get_processed_data(self):
        """Returns processed data as a list of dictionaries for MongoDB storage"""
     
        if "_id" in self.data.columns:
            self.data.drop(columns=["_id"], inplace=True)

            # ✅ Drop all rows that contain `NaT` before storing in MongoDB
        self.logger.info(f"Original data shape before dropping NaT: {self.data.shape}")
        self.data.dropna(inplace=True)
        self.logger.info(f"Data shape after dropping NaT rows: {self.data.shape}")

        # 2) Assign new unique IDs for every row
        self.data["_id"] = [str(uuid.uuid4()) for _ in range(len(self.data))]

        
        return self.data.to_dict(orient="records")  # Convert DataFrame to list of dicts
    
    @abstractmethod
    def preprocess(self):
        pass
    
    @abstractmethod
    def feature_engineering(self):
        pass

    @abstractmethod
    def save_to_database(self):
        
        pass
