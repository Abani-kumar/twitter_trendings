import os
import uuid
from datetime import datetime
import requests
import time
import sys
import logging
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
import chromedriver_autoinstaller
import pymongo
from dotenv import load_dotenv
import re

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_trending_topics(username, password):
    # MongoDB setup
    mongodb_url = os.getenv("MONGODB_URL")
    client = pymongo.MongoClient(mongodb_url)
    db = client["twitter_trends"]
    collection = db["trends"]

    # Selenium setup
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    chromedriver_autoinstaller.install()  # Ensure chromedriver is installed
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)

    try:
        # Twitter login
        print('inside')
        login_to_twitter(driver, username, password)
        # Fetch trending topics
        trends = WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, '//*[@class="css-175oi2r r-16y2uox r-bnwqim"]')))
        if not trends:
            raise TimeoutException
        top_trends = [trend.text for trend in trends[:5]]

        # Get current IP
        ip_response = requests.get("http://ip-api.com/json")
        ip_address = ip_response.json()["query"]

        # Store the data in MongoDB
        unique_id = str(uuid.uuid4())
        end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = {
            "_id": unique_id,
            "trend1": top_trends[0].replace("\n", " - "),
            "trend2": top_trends[1].replace("\n", " - "),
            "trend3": top_trends[2].replace("\n", " - "),
            "trend4": top_trends[3].replace("\n", " - "),
            "trend5": top_trends[4].replace("\n", " - "),
            "end_time": end_time,
            "ip_address": ip_address
        }
        collection.insert_one(data)

        return data

    except (TimeoutException, NoSuchWindowException) as e:
        logger.error(f"Error: {e}")
        raise  # Reraise the exception for higher-level handling

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise  # Reraise the exception for higher-level handling

    finally:
        driver.quit()

def login_to_twitter(driver,username, password):
    # Twitter login URL
    url = "https://twitter.com/i/flow/login"
    driver.get(url)

    # Log in to Twitter
    username = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[autocomplete="username"]')))
    username.send_keys(username)
    username.send_keys(Keys.ENTER)

    password = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[name="password"]')))
    password.send_keys(password)
    password.send_keys(Keys.ENTER)

    # Wait for the home page to load
    time.sleep(10)

if __name__ == "__main__":
    try:
        # Get username and password from command line arguments or any other source
        username = "your_username"
        password = "your_password"

        trends_data = fetch_trending_topics(username, password)
        logger.info(trends_data)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)  # Exit script with error code 1
