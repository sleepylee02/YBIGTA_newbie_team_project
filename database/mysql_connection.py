from sqlalchemy import create_engine
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

DB_URL = f'mysql+pymysql://{user}:{passwd}@{host}:{port}/{db}?charset=utf8'

engine = create_engine(DB_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()