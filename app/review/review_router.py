from fastapi import APIRouter, HTTPException
from database.mongodb_connection import get_mongo_db, preprocess_data_and_store  # ✅ MongoDB 연결 함수 가져오기
from database.mongodb_connection import PREPROCESS_CLASSES 

review = APIRouter(prefix="/api/review")  # ✅ `/api/review` prefix 추가

# MongoDB에 연결
db = get_mongo_db()

@review.post("/review/preprocess/{site_name}")

async def preprocess_review(site_name: str):
    """ API Endpoint to preprocess data for a given review site """
    if site_name not in PREPROCESS_CLASSES:
        raise HTTPException(status_code=400, detail="Invalid site name. Choose from: reviews_kakao, reviews_google, reviews_diningcode")
    
    result = preprocess_data_and_store(site_name)
    return result