import os
import time
import pandas as pd
import sys
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from utils.logger import setup_logger
from review_analysis.crawling.base_crawler import BaseCrawler

class ReviewCrawler(BaseCrawler):
    """
    A web crawler to scrape review data from Kakao Map.

    Attributes:
        output_dir (str): Directory to save the scraped data.
        logger (logging.Logger): Logger for logging messages.
        base_url (str): The base URL of the Kakao Map page to scrape.
        driver (WebDriver): Selenium WebDriver instance.
        data (pd.DataFrame): DataFrame containing the scraped reviews
    """

    def __init__(self, output_dir: str):
        """
        Initialize the ReviewCrawler with the specified output directory.

        Args:
            output_dir (str): Directory to save the scraped data.
        """
        super().__init__(output_dir)
        self.base_url = "https://place.map.kakao.com/17733090"
        self.driver = None
        log_file = os.path.join(output_dir, "review_crawler.log")
        self.logger = setup_logger(name="ReviewCrawler", log_file=log_file)
        self.data: pd.DataFrame = pd.DataFrame() 

    def start_browser(self):
        """
        Initialize and start the Selenium WebDriver.

        Raises:
            Exception: If the browser fails to start.
        """
        self.logger.info("Starting the browser...")
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--disable-gpu')
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
            self.logger.info("Browser started successfully.")
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise

    def scrape_reviews(self):
        """
        Scrape reviews and ratings from Kakao Map.

        Steps:
            1. Navigate to the base URL.
            2. Click the "More" button to load additional reviews.
            3. Parse the loaded page with BeautifulSoup.
            4. Extract dates, scores, and review texts.
            5. Save the extracted data to the database.

        Raises:
            Exception: If the browser is not started.
        """
        self.start_browser()
        
        try:
            self.logger.info("Navigating to the website...")
            self.driver.get(self.base_url)
            time.sleep(2)

            for i in range(500):
                try:
                    more_button = self.driver.find_element(By.XPATH, '//*[@id="mArticle"]/div[8]/div[3]/a/span[1]')
                    more_button.click()
                    self.logger.info(f"Clicked 'More' button: {i+1} times.")
                    time.sleep(1)
                except Exception as e:
                    self.logger.info("All reviews loaded or 'More' button not found. Parsing data...")
                    break

            # Parse reviews and ratings
            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            
            dates = []
            scores = []
            reviews = []

            review_items = soup.select("ul.list_evaluation > li")

            for item in review_items:
                try:
                    date = item.find("span", class_="time_write").get_text(strip=True)
                except AttributeError:
                    date = None  
                dates.append(date)

                try:
                    style = item.find("span", class_="ico_star inner_star")["style"]
                    width = int(style.split(":")[1].replace("%", "").replace(';',"").strip())  
                    score = width / 20  
                except (AttributeError, IndexError, ValueError):
                    score = None  
                scores.append(score)

                try:
                    review = item.find("p", class_="txt_comment").find("span").get_text(strip=True)
                    if review == "":
                        review = None  
                except AttributeError:
                    review = None  
                reviews.append(review)

            # Save data to a DataFrame
            self.logger.info(f"Scraped {len(scores)} reviews.")
            self.data = pd.DataFrame({"date": dates, "score": scores, "review": reviews})
            self.save_to_database()
        
        finally:
            self.logger.info("Closing the browser...")
            if self.driver:
                self.driver.quit()
                self.logger.info("Browser closed.")

    def save_to_database(self) -> None:
        """
        Save the scraped reviews to a CSV file.

        Raises:
            Exception: If saving the file fails.
        """
        self.logger.info("Saving data to the output directory...")
        try:
            os.makedirs(self.output_dir, exist_ok=True)
            file_path = os.path.join(self.output_dir, 'reviews_kakao.csv') 

            self.data.to_csv(file_path, index=False, encoding='utf-8-sig')

            self.logger.info(f"Data saved successfully at {file_path}.")
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")
            raise
