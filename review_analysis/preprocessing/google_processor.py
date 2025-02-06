import pandas as pd
import os
import re
import logging
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer # type : ignore
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from review_analysis.preprocessing.base_processor import BaseDataProcessor
from kiwipiepy import Kiwi # type : ignore

class GoogleProcessor(BaseDataProcessor):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.data = None
        self.kiwi = Kiwi()

    def preprocess(self):
        """
        데이터 전처리:
        1) CSV 읽기
        2) 결측치 제거
        3) 별점 유효성 검사 및 처리
        4) 텍스트 전처리 (processed_text 생성)
        """
        try:
            self.data = pd.read_csv(self.input_path)
            self.logger.info(f"Reading data from {self.input_path}")
        except Exception as e:
            self.logger.error(f"Failed to read input file: {e}")
            raise

        self.logger.info("Starting preprocessing")

        # 결측치 제거
        self.data = self.data.dropna(subset=['review_text', 'star_rating', 'review_date'])
        self.logger.info(f"Dropped rows with missing values. Remaining rows: {len(self.data)}")

        # 별점 유효성 검사 (1~5 범위 유지)
        self.data['star_rating'] = pd.to_numeric(self.data['star_rating'], errors='coerce')
        self.data = self.data[(self.data['star_rating'] >= 1) & (self.data['star_rating'] <= 5)]
        self.logger.info(f"Filtered invalid star ratings. Remaining rows: {len(self.data)}")

        # # 텍스트 전처리
        # self.data['processed_text'] = self.data['review_text'].apply(self.clean_text)
        # self.logger.info("Completed text preprocessing")

    # def clean_text(self, text: str):
    #     """
    #     한글 텍스트에서 특수문자 제거, Kiwi를 이용해 명사(NN)만 추출 (길이 2자 이상).
    #     """
    #     if not isinstance(text, str):
    #         text = ''
    #     # 특수문자 제거
    #     filtered_content = re.sub(r'[^\s\w\d]', ' ', text)
    #     # Kiwi 토큰화
    #     kiwi_tokens = self.kiwi.tokenize(filtered_content)
    #     # 명사(NN)이면서 길이 2 이상인 단어만 추출
    #     noun_words = [token.form for token in kiwi_tokens if 'NN' in token.tag and len(token.form) > 1]
    #     return " ".join(noun_words)

    # def feature_engineering(self):
    #     """
    #     피처 엔지니어링:
    #     1) TF-IDF 벡터화
    #     """
    #     self.logger.info("Starting feature engineering")
    #     try:
    #         # TF-IDF 벡터화
    #         vectorizer = TfidfVectorizer(max_features=100)
    #         tfidf_matrix = vectorizer.fit_transform(self.data['processed_text'])
    #         tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
    #         self.logger.info("TF-IDF vectorization completed.")

    #         # 원본 데이터와 결합
    #         self.data = pd.concat([self.data, tfidf_df], axis=1)
    #         self.logger.info("Concatenated TF-IDF features with original data.")
    #     except Exception as e:
    #         self.logger.error(f"Feature engineering failed: {e}")
    #         raise

    def save_to_database(self):
        """
        최종 CSV 저장
        """
        self.logger.info("Starting data saving")
        output_file = os.path.join(self.output_dir, 'preprocessed_reviews_google.csv')
        self.data.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data saved successfully at {output_file}.")