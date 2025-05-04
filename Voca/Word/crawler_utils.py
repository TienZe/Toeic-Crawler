import requests as req
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from multiprocessing import Process
import math
import undetected_chromedriver as uc
from html import unescape
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

domain = "https://www.vocabulary.com"

IPs = [
    "2001:0db8:85a3:0000:0000:8a2e:0370:7334",
    "2a03:2880:f031:0022:face:b00c:0000:0002",
    "2620:0:1cfe:face:b00c:0000:0000:0003",
    "2001:4860:4860:0000:0000:0000:0000:8888",
    "2a02:26f0:2b00:5a01:0000:0000:0000:0001",
    "2606:4700:4700:0000:0000:0000:0000:1111",
    "2001:0db8:0000:0000:0000:ff00:0042:8329",
    "2620:0:2d0:2df::15",
    "2a00:1450:4017:0803:0000:0000:0000:200e",
    "2600:1f16:1158:9901:5d4b:e2f3:4d07:80e1"
]

def  get_url(path):
    return domain + path

def init_driver():
    chrome_options = uc.ChromeOptions()
    # chrome_options.add_argument('--headless')  # Run in headless mode
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')  # Disable GPU hardware acceleration
    # chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    
    
    # Add X-Forwarded-For header
    # chrome_options.add_argument(f'--proxy-server=socks5://{random.choice(IPs)}:9999')
    
    driver = uc.Chrome(options=chrome_options, user_multi_procs=True)
    driver.set_page_load_timeout(25)

    return driver

def get_request(url, driver, save_path=None, wait=None, wait_for_presence=None, to_soup=True):
    try:
        driver.get(url)
    except Exception as e:
        error_message = str(e)
        print(f"Error loading page: {error_message}")
        
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
    
    if wait_for_presence:
        wait_driver = WebDriverWait(driver, 10)
        wait_driver.until(EC.presence_of_element_located((By.CSS_SELECTOR, wait_for_presence)))
        
    # Parse HTML
    if to_soup:
        soup = page_source_2_soup(driver.page_source)
        
        if save_path:
            with open(save_path, "w", encoding='utf-8') as f:
                f.write(soup.prettify())
                
        return soup
    
    return driver
    
def split_df_into_chunks(df, total_chunk):
    chunk_size = math.ceil(len(df) / total_chunk)
    chunks = [df[i:i+chunk_size] for i in range(0, df.shape[0], chunk_size)]
    
    return chunks


def page_source_2_soup(page_source):
    soup = BeautifulSoup(page_source, "html.parser")
    return soup

def save_chunks(chunks, output_dir):
    for index, chunk in enumerate(chunks):
        # Create the directory if it doesn't exist
        os.makedirs(f"{output_dir}/{index}", exist_ok=True)
        output_path = f"{output_dir}/{index}/input.csv"
        
        chunk.to_csv(output_path, index=False)
        print(f"Saved chunk {index} to {output_path}")
        

def beep():
    # play sound beep
    os.system('afplay /System/Library/Sounds/Glass.aiff')