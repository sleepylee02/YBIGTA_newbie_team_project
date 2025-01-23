from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
from review_analysis.crawling.utils.logger import setup_logger
import os


class DiningCrawler(BaseCrawler):
    def __init__(self, output_dir: str):
        super().__init__(output_dir)
        self.base_url = 'https://www.diningcode.com/profile.php?rid=LtMjLaf0kZJC'

        log_file = os.path.join(output_dir, "crawler.log")
        self.logger = setup_logger("DiningCrawler", log_file)
        
    def start_browser(self):
        self.logger.info("브라우저 시작 중...")
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.driver.get(self.base_url)
        time.sleep(5)
        self.logger.info("브라우저 시작 완료")
    
    def scrape_reviews(self):
        self.start_browser()
        self.logger.info("브라우저 시작 완료")
        while True:
            try:
                # "더보기" 버튼 찾기
                more_button = self.driver.find_element(By.CLASS_NAME, "More__Review__Button")
                
                # 버튼 클릭
                more_button.click()
                time.sleep(2)  # 페이지가 로드될 시간을 기다림

            except NoSuchElementException:
                self.logger.info("더 이상 '더보기' 버튼이 없습니다.")
                break

            except ElementClickInterceptedException:
                self.logger.warning("버튼 클릭이 방해받았습니다. 재시도 중...")
                time.sleep(2)  # 잠시 대기 후 다시 시도

            except ElementNotInteractableException:
                self.logger.warning("더보기 버튼이 현재 상호작용할 수 없는 상태입니다.")
                break

        self.logger.info("더보기 확장 완료")

        # BeautifulSoup으로 페이지 파싱
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        # Selenium 드라이버 종료
        self.driver.quit()

        # 데이터 저장 리스트 초기화
        stars = []
        dates = []
        comments = []

        # 리뷰 섹션 탐색
        main_div = soup.find("div", id="div_review")  # id가 "div_review"인 태그 찾기

        # 작은 div_review_* 찾기
        review_divs = main_div.find_all("div", id=lambda x: x and x.startswith("div_review_"))

        for review in review_divs:
            # 별점 추출
            star = review.find("span", class_="total_score")  
            stars.append(star.text.strip() if star else np.nan)

            # 날짜 추출
            date = review.find("div", class_="date")  
            dates.append(date.text.strip() if date else np.nan)

            # 댓글 추출
            comment = review.find("p", class_="review_contents btxt")  
            comments.append(comment.text.strip() if comment else np.nan)

        # DataFrame 생성
        self.reviews_df = pd.DataFrame({
            "Star": stars,
            "Date": dates,
            "Comment": comments
        })
        self.logger.info("리뷰 스크래핑 완료")
    
    def save_to_database(self):
        self.logger.info("데이터 저장 시작")
        # CSV 파일로 저장
        output_path = f"{self.output_dir}/reviews_diningcode.csv"
        self.reviews_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        self.logger.info(f"데이터가 {output_path}에 저장되었습니다.")