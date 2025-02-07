from base_processor import BaseDataProcessor
import pandas as pd
import os
import re
import logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer # type : ignore
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from kiwipiepy import Kiwi # type : ignore
import os


class KakaoProcessor(BaseDataProcessor):
    """
    Kakao 리뷰용 전처리 클래스.
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.data = None
        # Stopwords 불러오기
        current_dir = os.path.dirname(os.path.abspath(__file__))  # This gets the directory of kakao_processor.py
        stopwords_path = os.path.join(current_dir, 'stopwords-ko.txt')
        with open(stopwords_path, 'r', encoding='utf-8') as f:
            self.stopwords = [line.strip() for line in f.readlines()]

        # Kiwi 초기화 
        self.kiwi = Kiwi()

    def preprocess(self):
        """
        1) CSV 읽기
        2) 결측치 제거 (score, date, review)
        3) score 범위(1~5) 필터링
        4) date 파싱 & 최근 5년 범위 필터링
        5) clean_text (Kiwi + stopwords 등) 후 글자수 필터
        """
        # 1) CSV 읽기
        self.data = pd.read_csv(self.input_path)
        self.logger.info(f"Original data shape: {self.data.shape}")

        # 2) 결측치 처리
        self.data['review'].replace('', pd.NA, inplace=True)
        self.data = self.data.dropna(subset=['score', 'date', 'review'])
        self.logger.info(f"Data shape after dropping NaNs: {self.data.shape}")

        # 3) score 필터링 (1~5)
        self.data['score'] = pd.to_numeric(self.data['score'], errors='coerce')
        self.data = self.data.dropna(subset=['score'])
        self.logger.info(f"Data shape after converting 'score' to numeric: {self.data.shape}")

        self.data = self.data[(self.data['score'] >= 1) & (self.data['score'] <= 5)]
        self.logger.info(f"Data shape after removing invalid scores: {self.data.shape}")

        # 4) date 파싱 & 최근 5년 필터
        self.data['date'] = pd.to_datetime(self.data['date'], format='%Y.%m.%d.', errors='coerce')
        self.data = self.data.dropna(subset=['date'])
        self.logger.info(f"Data shape after date parsing: {self.data.shape}")

        current_date = datetime.now()
        self.data = self.data[
            (self.data['date'] >= current_date - pd.DateOffset(years=5)) &
            (self.data['date'] <= current_date)
        ]
        self.logger.info(f"Data shape after filtering dates within 5 years: {self.data.shape}")

        # 5) 텍스트 전처리(Kiwi + stopwords) 후 길이 필터
        self.data['clean_review'] = self.data['review'].apply(self.clean_text)
        self.logger.info("Completed text cleaning with Kiwi + stopwords removal.")

        self.data['clean_review_length'] = self.data['clean_review'].apply(len)
        initial_shape = self.data.shape
        self.data = self.data[self.data['clean_review_length'] >= 5]
        self.logger.info(
            f"Data shape after filtering 'clean_review' length >= 5: {self.data.shape} "
            f"(Removed {initial_shape[0] - self.data.shape[0]} rows)"
        )

        self.data = self.data[self.data['clean_review'].str.strip() != '']
        self.logger.info(f"Data shape after removing empty 'clean_review': {self.data.shape}")

    def feature_engineering(self):
        """
        1) 요일 컬럼(day_of_week)
        2) 주말여부 컬럼(is_weekend)
        3) 월(month)
        """
        self.data['day_of_week'] = self.data['date'].dt.day_name()
        self.data['is_weekend'] = self.data['date'].dt.dayofweek >= 5  # 토(5), 일(6)
        self.data['month'] = self.data['date'].dt.month

        self.logger.info("Feature engineering completed.")

    def save_to_database(self):
        """
        1) TF-IDF 벡터화 (clean_review)
        2) 최종 CSV 저장
        """
        # TF-IDF 벡터화
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform(self.data['clean_review'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        self.logger.info("TF-IDF vectorization completed.")

        # Concatenate TF-IDF features
        final_data = pd.concat([self.data, tfidf_df], axis=1)
        self.logger.info("Concatenated TF-IDF features with original data.")

        # Save to CSV
        output_file = os.path.join(self.output_dir, 'preprocessed_reviews_kakao.csv')
        final_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data saved successfully at {output_file}.")

    def clean_text(self, text: str) -> str:
        """
        기존 KakaoProcessor + GoogleProcessor(키위) 로직을 결합한 텍스트 전처리:
          1) 문자열 체크
          2) 특수문자 제거 (공백, 단어문자, 숫자만 남김)
          3) Kiwi 토큰화 -> 'NN' 태그이면서 길이 >= 2인 단어만 추출
          4) Stopwords 제거
          5) 최종 문자열 반환
        """
        if not isinstance(text, str):
            text = ''

        # (GoogleProcessor) 특수문자 제거: [^\s\w\d]
        filtered_content = re.sub(r'[^\s\w\d]', ' ', text)

        # Kiwi 토큰화 & 명사(NN) 추출
        kiwi_tokens = self.kiwi.tokenize(filtered_content)
        noun_tokens = [token.form for token in kiwi_tokens if ('NN' in token.tag) and (len(token.form) > 1)]

        # Stopwords 제거
        if self.stopwords:
            noun_tokens = [word for word in noun_tokens if word not in self.stopwords]

        # 최종 문자열
        return " ".join(noun_tokens)