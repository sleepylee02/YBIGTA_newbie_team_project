from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
port = os.getenv("DB_PORT","3306") 
db = os.getenv("DB_NAME")

if not all([user, passwd, host, port, db]):
    raise ValueError("[ERROR] 환경 변수(DB 설정)가 올바르게 설정되지 않았습니다. .env 파일을 확인하세요.")


DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

try:
    engine = create_engine(DB_URL, echo=True, pool_pre_ping=True)
    print("Successfully created database engine!")
except Exception as e:
    print(f"[ERROR] Database engine creation failed: {e}")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def test_db_connection():
    """ DB 연결 테스트 함수 """
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection test passed!")
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")

# ✅ 실행 시 DB 연결 체크
if __name__ == "__main__":
    test_db_connection()