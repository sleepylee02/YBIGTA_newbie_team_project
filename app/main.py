from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.review.review_router import review  # ✅ 추가
from app.user.user_router import user
from app.config import PORT

import uvicorn
import os


app = FastAPI()

static_path = os.path.join(os.path.dirname(__file__), "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

app.include_router(user)
app.include_router(review)

if __name__=="__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=True)
