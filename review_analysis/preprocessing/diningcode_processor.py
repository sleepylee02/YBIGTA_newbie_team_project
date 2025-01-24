from review_analysis.preprocessing.base_processor import BaseDataProcessor
import os
import pandas as pd
from utils.logger import setup_logger
import re
from kiwipiepy import Kiwi
from sklearn.feature_extraction.text import TfidfVectorizer


class DiningcodeProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        self.input_path = input_path
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Logger 초기화
        log_file = os.path.join(output_dir, "DiningProcessor.log")
        self.logger = setup_logger(log_file)

        # 데이터 읽기 메서드 호출
        self.df = self._read_input()

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

    # 이하 메서드는 변경 없이 유지
    def preprocess(self):
        self.logger.info(f"Reading data from {self.input_path}")
        self.logger.info("Starting preprocessing")
        try:
            # Convert date column
            self.df['Date'] = pd.to_datetime(self.df['Date'].str.replace("년", "-")
                                            .str.replace("월", "-")
                                            .str.replace("일", "")
                                            .str.strip(), 
                                    errors='coerce')

            # Log missing data counts
            missing_count = self.df.isnull().sum()
            self.logger.info("Missing values per column:")
            self.logger.info(missing_count)

            # Drop rows with missing values
            self.df_cleaned = self.df.dropna()
            self.logger.info(f"Dropped rows with missing values. Remaining rows: {len(self.df_cleaned)}")

            # Ensure 'Star' column is treated as string for .str.extract()
            self.df_cleaned["Star"] = (
                self.df_cleaned["Star"]
                .astype(str)  # Convert to string
                .str.extract(r"(\d+)")  # Extract numeric values
                .fillna(0)  # Replace NaN with 0 (or drop NaN if preferred)
                .astype(int)  # Convert to integer
            )

            # Korean text preprocessing
            kiwi = Kiwi()

            def do_Kr_preprocessing(text):
                filtered_content = re.sub('[^\s\w\d]', ' ', text)
                kiwi_tokens = kiwi.tokenize(filtered_content)
                Noun_words = [token.form for token in kiwi_tokens if 'NN' in token.tag and len(token.form) > 1]
                return " ".join(Noun_words)

            self.df_cleaned['processed_text'] = self.df_cleaned['Comment'].apply(do_Kr_preprocessing)

            self.logger.info("Preprocessing completed")
        except Exception as e:
            self.logger.error(f"Preprocessing failed: {e}")
            raise

    def feature_engineering(self):
        self.logger.info("Starting feature engineering")
        try:
            self.df_cleaned['day_of_week'] = self.df_cleaned['Date'].dt.day_name()
            self.df_cleaned['is_weekend'] = self.df_cleaned['Date'].dt.dayofweek >= 5
            self.df_cleaned['month'] = self.df_cleaned['Date'].dt.month
            self.logger.info("Feature engineering completed")
            vectorizer = TfidfVectorizer(max_features=100)
            tfidf_matrix = vectorizer.fit_transform(self.df_cleaned['processed_text'])
            tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
            self.logger.info("TF-IDF vectorization completed.")
            self.final_data = pd.concat([self.df_cleaned, tfidf_df], axis=1)
            self.logger.info("Concatenated TF-IDF features with original data.")
        except Exception as e:
            self.logger.error(f"Feature engineering failed: {e}")
            raise

    def save_to_database(self):
        self.logger.info("데이터 저장 시작")
        output_file = os.path.join(self.output_dir, 'preprocessed_reviews_diningcode.csv')
        self.final_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data saved successfully at {output_file}.")