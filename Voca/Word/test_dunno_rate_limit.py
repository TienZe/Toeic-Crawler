from crawler_utils import *
import requests as req
import random
import json
import time


def get_dunno_api(url, driver):
    try:
        soup = get_request(url, driver)
        return soup
        # json_str = soup.select_one("pre").text.strip()
        # return json.loads(json_str)
    except Exception as e:
        print(f"429 Too many requests, wait for 10 seconds {e}")
        time.sleep(30)
        return get_dunno_api(url, driver)
        
        
def test_dunno_rate_limit():
    try:
        driver = init_driver()
        num_of_call = 100

        for i in range(num_of_call):
            # data =get_url("https://api.dunno.ai/api/search/en/envi/combination?limit=1&page=1")
            # data = get_dunno_api("https://api.dunno.ai/api/search/en/envi/combination?limit=1&page=1", driver)
            data = get_dunno_api("https://dunno.ai/search/word/combination?hl=vi&api=1", driver)
            
            if i % 10 == 0:
                print(f"Call request {i}")
    finally:
        driver.quit()

