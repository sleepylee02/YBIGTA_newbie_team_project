import os
import sys
import time
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timedelta
from typing import Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from utils.logger import setup_logger
from review_analysis.crawling.base_crawler import BaseCrawler

class GoogleMapsCrawler(BaseCrawler):
    """
    Google Maps 리뷰 데이터를 크롤링하는 클래스.

    Attributes:
        base_url (str): 크롤링할 대상 Google Maps URL.
        output_dir (str): 크롤링한 데이터를 저장할 디렉토리 경로.
        driver (Optional[webdriver.Chrome]): Selenium WebDriver 인스턴스.
    """

    def __init__(self, output_dir: str):
        """
        GoogleMapsCrawler 객체를 초기화합니다.

        Args:
            base_url (str): 크롤링할 대상 Google Maps URL.
            output_dir (str): 크롤링한 데이터를 저장할 디렉토리 경로.
        """
        super().__init__(output_dir)
        self.base_urls = ["https://www.google.com/maps/place/%EC%84%B1%EC%8B%AC%EB%8B%B9+DCC%EC%A0%90/data=!4m8!3m7!1s0x3565498ff8570165:0x8cd47008647df355!8m2!3d36.3753313!4d127.3924207!9m1!1b1!16s%2Fg%2F11f0kvfpj0?entry=ttu&g_ep=EgoyMDI1MDEyMS4wIKXMDSoASAFQAw%3D%3D",
                          "https://www.google.com/maps/place/Sungsimdang+Bakery+Lotte+Daejeon+Branch/data=!4m8!3m7!1s0x3565495a46274a79:0x5b973bd3cfd7d125!8m2!3d36.3403653!4d127.3901764!9m1!1b1!16s%2Fg%2F1ptxmrrlz?entry=ttu&g_ep=EgoyMDI1MDEyMS4wIKXMDSoASAFQAw%3D%3D",
                          "https://www.google.com/maps/place/%EC%84%B1%EC%8B%AC%EB%8B%B9+%EB%B3%B8%EC%A0%90/data=!4m8!3m7!1s0x356548d8f73d355d:0x69e930d902c95eca!8m2!3d36.3276832!4d127.4273424!9m1!1b1!16s%2Fg%2F1tct_8rr?entry=ttu&g_ep=EgoyMDI1MDEyMC4wIKXMDSoASAFQAw%3D%3D"
                          ]
        log_file = os.path.join(output_dir, "google_maps_crawler.log")
        self.logger = setup_logger(name="GoogleMapsCrawler", log_file=log_file)

    def start_browser(self, url : str) -> None:
        """
        Selenium WebDriver를 초기화하고 브라우저를 시작합니다.

        Raises:
            Exception: 브라우저 초기화 실패 시 발생.
        """
        self.logger.info("브라우저를 시작합니다.")
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.get(url)
        self.driver.implicitly_wait(3)
        time.sleep(3)
        self.logger.info("브라우저가 성공적으로 시작되었습니다.")

    def scrape_reviews(self, max_reviews: int = 1000) -> pd.DataFrame:
        """
        Google Maps 리뷰 데이터를 크롤링합니다.

        Args:
            max_reviews (int): 수집할 최대 리뷰 수. 기본값은 1000.

        Returns:
            pd.DataFrame: 수집된 리뷰 데이터를 포함하는 데이터프레임.
        """
        all_reviews = []
        for url in self.base_urls:
            self.start_browser(url)
            try:
                # 스크롤 영역 탐색
                self.logger.info("스크롤 영역을 탐색합니다.")
                scrollable_div = self.driver.find_element(By.XPATH, '//div[contains(@class, "m6QErb") and contains(@class, "DxyBCb") and contains(@class, "kA9KIf")]')

                # 스크롤 수행
                for i in range(100):
                    self.logger.info(f"스크롤 {i+1}/100 진행 중...")
                    self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
                    time.sleep(1)

                # 최상단으로 이동
                self.logger.info("최상단으로 이동합니다.")
                self.driver.execute_script("arguments[0].scrollTo(0, 0)", scrollable_div)
                time.sleep(1)

                # '더보기' 버튼 클릭
                self.logger.info("'더보기' 버튼 클릭을 시작합니다.")
                more_buttons = self.driver.find_elements(By.XPATH, '//button[contains(@class, "w8nwRe") and contains(@class, "kyuRq")]')
                for button in more_buttons:
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", button)
                        button.click()
                    except Exception:
                        self.logger.warning("'더보기' 버튼 클릭 실패.")

                # HTML 파싱
                self.logger.info("HTML 데이터를 파싱합니다.")
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                review_elements = soup.find_all("div", class_="jftiEf")
                today = datetime.now()

                # 리뷰 데이터 추출
                for element in review_elements:
                    try:
                        review_text_element = element.find("span", class_="wiI7pd")
                        review_text = review_text_element.text.strip() if review_text_element else "N/A"

                        star_rating_element = element.find("span", role="img")
                        star_rating = star_rating_element.get("aria-label").split(" ")[1].replace("개", "") if star_rating_element else "N/A"

                        review_date_element = element.find("span", class_="rsqaWe")
                        raw_date = review_date_element.text.strip() if review_date_element else "N/A"

                        # 날짜 변환
                        if "일 전" in raw_date:
                            days_ago = int(raw_date.replace("일 전", "").strip())
                            review_date = (today - timedelta(days=days_ago)).strftime("%Y.%m.%d")
                        elif "주 전" in raw_date:
                            weeks_ago = int(raw_date.replace("주 전", "").strip())
                            review_date = (today - timedelta(weeks=weeks_ago)).strftime("%Y.%m.%d")
                        elif "달 전" in raw_date:
                            months_ago = int(raw_date.replace("달 전", "").strip())
                            review_date = (today - timedelta(days=months_ago * 30)).strftime("%Y.%m.%d")
                        elif "년 전" in raw_date:
                            years_ago = int(raw_date.replace("년 전", "").strip())
                            # Adjust the year and keep the same month and day as today
                            try:
                                review_date = today.replace(year=today.year - years_ago).strftime("%Y.%m.%d")
                            except ValueError:
                                review_date = (today - timedelta(days=years_ago * 365)).strftime("%Y.%m.%d")
                        else:
                            review_date = raw_date

                        all_reviews.append({
                            "review_text": review_text,
                            "star_rating": star_rating,
                            "review_date": review_date
                        })

                        if len(all_reviews) >= max_reviews:
                            break

                    except Exception as e:
                        self.logger.warning(f"리뷰 데이터 추출 실패: {e}")

                self.logger.info(f"총 {len(all_reviews)}개의 리뷰를 수집했습니다.")
                
            finally:
                if self.driver:
                    self.driver.quit()
                    self.logger.info("브라우저를 종료했습니다.")
                    
        self.data = pd.DataFrame(all_reviews)
        self.save_to_database()


    def save_to_database(self) -> None:
        """
        Save the scraped reviews to a CSV file.

        Raises:
            Exception: If saving the file fails.
        """
        self.logger.info("Saving data to the output directory...")
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            file_path = os.path.join(self.output_dir, 'reviews_google.csv') 

            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')

            self.logger.info(f"Data saved successfully at {file_path}.")
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise