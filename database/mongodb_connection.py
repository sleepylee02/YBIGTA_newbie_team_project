from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import pandas as pd
from typing import Dict, Type
from uuid import uuid4  
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import preprocessing classes
from review_analysis.preprocessing.base_processor import BaseDataProcessor
from review_analysis.preprocessing.kakao_processor import KakaoProcessor
from review_analysis.preprocessing.google_processor import GoogleProcessor
from review_analysis.preprocessing.diningcode_processor import DiningcodeProcessor

# Load environment variables
load_dotenv()
mongo_url = os.getenv("MONGO_URL")

# Connect to MongoDB
mongo_client = MongoClient(mongo_url)
mongo_db = mongo_client["smile"]

# Define preprocessing class mapping
PREPROCESS_CLASSES: Dict[str, Type[BaseDataProcessor]] = {
    "reviews_kakao": KakaoProcessor,
    "reviews_google": GoogleProcessor,
    "reviews_diningcode": DiningcodeProcessor
}

# FastAPI app
app = FastAPI()

def save_mongo_to_csv(documents, temp_csv_path):
    """ Converts MongoDB documents to a CSV file for processing """
    if not documents:
        return None

    df = pd.DataFrame(documents)

    # Remove MongoDB `_id` field
    if "_id" in df.columns:
        df.drop(columns=["_id"], inplace=True)

    df.to_csv(temp_csv_path, index=False, encoding="utf-8-sig")
    return temp_csv_path

def preprocess_data_and_store(collection_name: str):
    """ Queries MongoDB, preprocesses data, and stores it back into MongoDB. """
    collection = mongo_db[collection_name]
    processed_collection = mongo_db[f"{collection_name}_processed"]

    documents = list(collection.find())

    if not documents:
        raise HTTPException(status_code=404, detail=f"No data found in {collection_name}")

    if collection_name not in PREPROCESS_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid collection name")

    preprocessor_class = PREPROCESS_CLASSES[collection_name]
    output_dir = "processed_data"
    os.makedirs(output_dir, exist_ok=True)

    # Convert MongoDB data to a CSV file
    temp_csv_path = os.path.join(output_dir, f"{collection_name}.csv")
    temp_csv = save_mongo_to_csv(documents, temp_csv_path)
    if temp_csv is None:
        raise HTTPException(status_code=404, detail="No data available for preprocessing")

    # Preprocess data
    preprocessor = preprocessor_class(temp_csv, output_dir)
    preprocessor.preprocess()
    preprocessor.feature_engineering()

    # Store processed data back in MongoDB
    processed_data = preprocessor.get_processed_data()

    if processed_data:
        processed_collection.insert_many(processed_data)
    else:
        raise HTTPException(status_code=500, detail="Preprocessing produced no output")

    # Remove temporary CSV file
    os.remove(temp_csv_path)

    return {"message": f"Processed {len(processed_data)} documents and stored in {collection_name}_processed"}

@app.post("/review/preprocess/{site_name}")
async def preprocess_review(site_name: str):
    """ API Endpoint to preprocess data for a given review site """
    if site_name not in PREPROCESS_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid site name. Choose from: reviews_kakao, reviews_google, reviews_diningcode")
    
    result = preprocess_data_and_store(site_name)
    return result