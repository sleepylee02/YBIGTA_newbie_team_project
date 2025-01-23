from review_analysis.preprocessing.base_processor import BaseDataProcessor
import pandas as pd
import os
import re
import logging
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


class KakaoProcessor(BaseDataProcessor):
    def __init__(self, input_path: str, output_dir: str):
        super().__init__(input_path, output_dir)
        self.data = None
        with open('stopwords-ko.txt', 'r', encoding='utf-8') as f:
            self.stopwords = [line.strip() for line in f.readlines()]
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    def preprocess(self):
        # Load data
        self.data = pd.read_csv(self.input_path)
        self.logger.info(f"Original data shape: {self.data.shape}")
        
        # Replace empty strings in 'review' with NaN and drop rows with missing 'score', 'date', or 'review'
        self.data['review'].replace('', pd.NA, inplace=True)
        self.data = self.data.dropna(subset=['score', 'date', 'review'])
        self.logger.info(f"Data shape after dropping NaNs: {self.data.shape}")
        
        # Convert 'score' to numeric if not already
        self.data['score'] = pd.to_numeric(self.data['score'], errors='coerce')
        self.data = self.data.dropna(subset=['score'])
        self.logger.info(f"Data shape after converting 'score' to numeric and dropping NaNs: {self.data.shape}")
        
        # Remove scores outside 1-5
        self.data = self.data[(self.data['score'] >= 1) & (self.data['score'] <= 5)]
        self.logger.info(f"Data shape after removing invalid scores: {self.data.shape}")
        
        # Handle date format and remove invalid dates
        self.data['date'] = pd.to_datetime(self.data['date'], format='%Y.%m.%d.', errors='coerce')
        self.data = self.data.dropna(subset=['date'])
        self.logger.info(f"Data shape after date parsing and dropping invalid dates: {self.data.shape}")
        
        # Remove dates older than 5 years from now
        current_date = datetime.now()
        self.data = self.data[(self.data['date'] >= current_date - pd.DateOffset(years=5)) & 
                              (self.data['date'] <= current_date)]
        self.logger.info(f"Data shape after filtering dates within 5 years: {self.data.shape}")
        
        # Clean text data
        self.data['clean_review'] = self.data['review'].apply(self.clean_text)
        self.logger.info("Completed text cleaning.")
        
        # Calculate 'clean_review' length and filter
        self.data['clean_review_length'] = self.data['clean_review'].apply(len)
        initial_shape = self.data.shape
        self.data = self.data[self.data['clean_review_length'] >= 5]
        self.logger.info(f"Data shape after filtering 'clean_review' length >= 5: {self.data.shape} (Removed {initial_shape[0] - self.data.shape[0]} rows)")
        
        # Drop reviews that are still empty after cleaning (redundant but safe)
        self.data = self.data[self.data['clean_review'].str.strip() != '']
        self.logger.info(f"Data shape after removing empty 'clean_review': {self.data.shape}")
        
    def feature_engineering(self):
        # Derived feature: day of week
        self.data['day_of_week'] = self.data['date'].dt.day_name()
        
        # Derived feature: is_weekend
        self.data['is_weekend'] = self.data['date'].dt.dayofweek >= 5  # 5 for Saturday, 6 for Sunday
        
        # Derived feature: month
        self.data['month'] = self.data['date'].dt.month
        
        self.logger.info("Feature engineering completed.")
        
    def save_to_database(self):
        # Vectorize text using TF-IDF
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform(self.data['clean_review'])
        tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())
        self.logger.info("TF-IDF vectorization completed.")
        
        # Concatenate TF-IDF features with original data
        final_data = pd.concat([self.data, tfidf_df], axis=1)
        self.logger.info("Concatenated TF-IDF features with original data.")
        
        # Save to CSV
        output_file = os.path.join(self.output_dir, 'preprocessed_reviews_kakao.csv')
        final_data.to_csv(output_file, index=False, encoding='utf-8-sig')
        self.logger.info(f"Data saved successfully at {output_file}.")
    
    def clean_text(self, text):
        # Ensure the text is a string
        if not isinstance(text, str):
            text = ''
        # Remove special characters and numbers
        text = re.sub(r'[^가-힣\s]', '', text)
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        # Strip leading and trailing spaces
        text = text.strip()
        # Remove stopwords
        if self.stopwords:
            text = ' '.join([word for word in text.split() if word not in self.stopwords])
        return text
