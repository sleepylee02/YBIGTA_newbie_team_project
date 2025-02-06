import os
import pandas as pd
import re
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer

from review_analysis.preprocessing.base_processor import BaseDataProcessor
from utils.logger import setup_logger


class DiningcodeProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Logger 초기화
        log_file = os.path.join(output_dir, "DiningProcessor.log")
        self.logger = setup_logger(log_file)

        # 데이터 읽기
        self.data = self._read_input()

    def _read_input(self):
        """
        CSV 파일을 읽어 DataFrame으로 반환하는 메서드.
        """
        try:
            self.logger.info(f"Reading input file: {self.input_path}")
            return pd.read_csv(self.input_path)
        except Exception as e:
            self.logger.error(f"Failed to read input file: {e}")
            raise

    def preprocess(self):
        """
        - 날짜 컬럼 정제
        - 누락값 처리
        - Star 컬럼 정수화
        - 한글 텍스트 전처리
        """
        self.logger.info(f"Reading data from {self.input_path}")
        self.logger.info("Starting preprocessing")
        try:
            # 1) 날짜 컬럼 정제
            self.data['Date'] = (
                self.data['Date']
                .str.replace("년", "-", regex=False)
                .str.replace("월", "-", regex=False)
                .str.replace("일", "", regex=False)
                .str.strip()
            )
            self.data['Date'] = pd.to_datetime(self.data['Date'], errors='coerce')

            # # 2) 누락값 처리
            # missing_count = self.data.isnull().sum()
            # self.logger.info("Missing values per column:")
            # self.logger.info(missing_count)

            # # DataFrame 자체를 정리해나가기 위해 dropna() 재할당
            # self.data = self.data.dropna()
            # self.logger.info(f"Dropped rows with missing values. Remaining rows: {len(self.data)}")

            # ✅ Drop rows with any NaT (missing values)
            self.logger.info(f"Original data shape: {self.data.shape}")
            self.data.dropna(subset=['Date'],inplace=True)  # ✅ Drop all rows with NaT values
            self.logger.info(f"Data shape after dropping NaT rows: {self.data.shape}")

            # 3) Star 컬럼에서 숫자만 추출하여 정수로 변환
            self.data["Star"] = (
                self.data["Star"]
                .astype(str)               # Convert to string
                .str.extract(r"(\d+)")    # Extract numeric portion
                .fillna(0)                # Replace NaN with 0 if no match
                .astype(int)              # Convert to integer
            )
        except Exception as e:
            self.logger.error(f"Preprocessing failed: {e}")
            raise
        
        # 서버 돌리기 위해서 오래 걸리는 프로세스 모두 제거

        #     # 4) 한글 텍스트 전처리
        #     kiwi = Kiwi()

        #     # def do_Kr_preprocessing(text):
        #     #     # 한글, 숫자, 공백, 알파벳, 숫자 이외는 모두 제거
        #     #     filtered_content = re.sub(r'[^\s\w\d]', ' ', text)
        #     #     kiwi_tokens = kiwi.tokenize(filtered_content)
        #     #     # 명사 태그(NN*) 추출, 길이가 1 이하인 토큰은 제외
        #     #     Noun_words = [token.form for token in kiwi_tokens if 'NN' in token.tag and len(token.form) > 1]
        #     #     return " ".join(Noun_words)

        #     def do_Kr_preprocessing(text):
        #         # ✅ Convert non-string values to strings
        #         if not isinstance(text, str):
        #             text = str(text)  # Convert NaN, floats, or numbers to string

        #         # ✅ Handle NaN values explicitly
        #         if text.lower() == "nan":  
        #             return ""

        #         # ✅ Remove special characters
        #         filtered_content = re.sub(r'[^\s\w\d]', ' ', text)

        #         kiwi_tokens = kiwi.tokenize(filtered_content)
        #         # 명사 태그(NN*) 추출, 길이가 1 이하인 토큰은 제외
        #         Noun_words = [token.form for token in kiwi_tokens if 'NN' in token.tag and len(token.form) > 1]

        #         return " ".join(Noun_words)

        #     self.data['processed_text'] = self.data['Comment'].apply(do_Kr_preprocessing)

        #     self.logger.info("Preprocessing completed")
        # except Exception as e:
        #     self.logger.error(f"Preprocessing failed: {e}")
        #     raise

    # def feature_engineering(self):
    #     """
    #     - 날짜 기반 파생변수 (요일, 주말여부, 월)
    #     - TF-IDF로 텍스트 벡터화
    #     """
    #     self.logger.info("Starting feature engineering")
    #     try:
    #         self.logger.info(f"Checking for NaT in 'Date' before feature engineering")
    #         self.data = self.data.dropna(subset=['Date'])

    #         # 날짜 기반 파생변수
    #         self.data['day_of_week'] = self.data['Date'].dt.day_name()
    #         self.data['is_weekend'] = self.data['Date'].dt.dayofweek >= 5
    #         self.data['month'] = self.data['Date'].dt.month

    #         # TF-IDF 벡터화
    #         vectorizer = TfidfVectorizer(max_features=100)
    #         tfidf_matrix = vectorizer.fit_transform(self.data['processed_text'])
    #         tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

    #         # 기존 self.data에 TF-IDF 특성 합치기
    #         self.data = pd.concat([self.data, tfidf_df], axis=1)

    #         self.logger.info("Feature engineering completed")
    #     except Exception as e:
    #         self.logger.error(f"Feature engineering failed: {e}")
    #         raise

    def save_to_database(self):
        """
        완성된 DataFrame(self.data)을 CSV로 저장.
        """
        self.logger.info("데이터 저장 시작")
        output_file = os.path.join(self.output_dir, 'preprocessed_reviews_diningcode.csv')
        self.data.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data saved successfully at {output_file}.")