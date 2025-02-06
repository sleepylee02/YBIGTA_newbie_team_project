# Python 3.9 이미지 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일만 복사 (`.dockerignore` 적용됨)
COPY requirements.txt requirements.txt
COPY . .

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 환경 변수 설정 (PYTHONPATH 추가)
ENV PYTHONPATH=/app

# Flask 포트 개방
EXPOSE 5000

# 컨테이너 실행 시 API 실행
CMD ["python", "app/main.py"]