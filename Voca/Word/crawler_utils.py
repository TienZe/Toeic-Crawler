import requests as req
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from multiprocessing import Process
import math
import undetected_chromedriver as uc
from html import unescape

domain = "https://www.vocabulary.com"

def  get_url(path):
    return domain + path

def init_driver():
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    
    driver = uc.Chrome(options=chrome_options, user_multi_procs=True)
    driver.set_page_load_timeout(10)

    return driver

def get_request(url, driver, save_path=None, wait=None):
    try:
        driver.get(url)
    except Exception as e:
        print(f"Error loading page: {e}")
        
        # Retry loading the page
        try:
            print('Retrying after 5 seconds ...')
            sleep(5)
            driver.get(url)
        except Exception as e:
            print(f"Retry failed: {e}")
            raise e
            
    # Wait for Cloudflare check to complete
    
    if "Cloudflare" in driver.page_source:
        print("Cloudflare verification...")
        sleep(10)
    
    if wait:
        sleep(wait)
        
    # Parse HTML
    soup = BeautifulSoup(driver.page_source, "html.parser")
    if save_path:
        with open(save_path, "w", encoding='utf-8') as f:
            f.write(soup.prettify())
    
    return soup

    