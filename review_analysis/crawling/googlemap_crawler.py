from bs4 import BeautifulSoup

from review_analysis.crawling.utils.logger import setup_logger
from review_analysis.crawling.base_crawler import BaseCrawler
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import pandas as pd

import time
import os


class GoogleMapsCrawler:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.base_url = "https://www.google.com/maps/place/%EC%84%B1%EC%8B%AC%EB%8B%B9+%EB%B3%B8%EC%A0%90/data=!4m8!3m7!1s0x356548d8f73d355d:0x69e930d902c95eca!8m2!3d36.3276832!4d127.4273424!9m1!1b1!16s%2Fg%2F1tct_8rr?entry=ttu&g_ep=EgoyMDI1MDEyMC4wIKXMDSoASAFQAw%3D%3D"
        self.driver = None

    def start_browser(self):
        """브라우저를 설정하고 시작합니다."""
        chrome_options = Options()
        chrome_options.add_experimental_option("detach", True)  # 브라우저 자동 종료 방지
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        chrome_options.add_argument("--start-maximized")

        # ChromeDriver 경로 설정
        chromedriver_path = r"C:\Users\SAMSUNG\Desktop\Downloads\chromedriver-win64\chromedriver.exe"

        service = Service(chromedriver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.get(self.base_url)
        self.driver.implicitly_wait(3)
        time.sleep(3)

    def scrape_reviews(self):
        """Google Maps 리뷰 데이터를 크롤링합니다."""
        all_reviews = []

        # 리뷰 스크롤 영역 탐색
        try:
            scrollable_div = self.driver.find_element(By.XPATH, '//div[contains(@class, "m6QErb") and contains(@class, "DxyBCb") and contains(@class, "kA9KIf")]')
        except Exception as e:
            print(f"[ERROR] 리뷰 스크롤 영역을 찾을 수 없습니다: {e}")
            return pd.DataFrame()

        # 스크롤 및 데이터 로드
        prev_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        collected_reviews = 0
        max_reviews = 1000

        while collected_reviews < max_reviews:
            self.driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
            time.sleep(2)  # 스크롤 후 로딩 대기
            curr_height = self.driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
            if curr_height == prev_height:
                break  # 더 이상 스크롤할 내용이 없음
            prev_height = curr_height

            # HTML 파싱
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            review_elements = soup.find_all("div", class_="jftiEf")

            for element in review_elements:
                try:
                    # "자세히" 버튼 클릭
                    try:
                        more_button = self.driver.find_element(By.XPATH, './/button[contains(@class, "w8nwRe") and contains(@class, "kyuRq")]')
                        more_button.click()
                        time.sleep(1)  # 클릭 후 텍스트 확장을 기다림
                    except Exception as e:
                        print(f"[INFO] '자세히' 버튼이 없습니다: {e}")

                    # 리뷰 텍스트
                    review_text = element.find("span", class_="wiI7pd").text.strip()

                    # 별점
                    star_rating_element = element.find("span", role="img")
                    if star_rating_element:
                        star_rating = star_rating_element.get("aria-label").split(" ")[1]  # 예: "별 5개"에서 "5개" 추출
                    else:
                        star_rating = "N/A"

                    # 날짜
                    review_date = element.find("span", class_="rsqaWe").text.strip()

                    all_reviews.append({
                        "review_text": review_text,
                        "star_rating": star_rating,
                        "review_date": review_date
                    })
                    collected_reviews += 1

                    if collected_reviews >= max_reviews:
                        break

                except Exception as e:
                    print(f"[WARNING] 리뷰 데이터 추출 실패 (원인: {e}): {element}")

            if collected_reviews >= max_reviews:
                break

        print(f"총 {len(all_reviews)}개의 리뷰를 수집했습니다.")
        return pd.DataFrame(all_reviews)

    def run(self):
        try:
            self.start_browser()
            df = self.scrape_reviews()
            return df
        finally:
            if self.driver:
                self.driver.quit()

if __name__ == "__main__":
    # 출력 디렉토리 설정
    output_directory = "output"

    # 크롤러 실행
    crawler = GoogleMapsCrawler(output_directory)
    df = crawler.run()
    print(df.head())
