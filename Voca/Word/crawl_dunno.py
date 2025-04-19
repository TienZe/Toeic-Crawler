from crawler_utils import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Function to extract network requests from logs
def extract_network_calls(logs):
    for log in logs:
        try:
            log_data = json.loads(log["message"])["message"]
            
            # Filter for Network.requestWillBeSent events
            if log_data["method"] == "Network.requestWillBeSent":
                request_url = log_data["params"]["request"]["url"]
                
                # Filter for dunno audio media calls
                if "https://data.dunno.ai/audios/example" in request_url:
                    print(f"Audio API call detected: {request_url}")
                    return request_url
        except Exception as e:
            return None
    return None


def get_audio_url(driver):
    # Wait for the the audio button loaded
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box-audio")))

    # Clear logs before interaction
    driver.get_log('performance')

    # Try different selectors to find audio button
    try:
        # Try to find an audio-related element using multiple selectors
        selector = ".box-audio"
        
        audio_element = driver.find_element(By.CSS_SELECTOR, selector)
        if audio_element:
            # Click the audio button
            audio_element.click()
            print("Clicked audio button")
            
            # Wait a moment for the request to be sent
            time.sleep(0.2)
            
            # Get performance logs
            logs = driver.get_log('performance')
            audio_url = extract_network_calls(logs)
            
            return audio_url
                
    except Exception as e:
        print(f"Error get audio url: {str(e)}")
        return None

def construct_dunno_search_url(word, lan):
    dunno_search_word_endpoint = "https://dunno.ai/search/word"
    
    return f"{dunno_search_word_endpoint}/{word}?hl={lan}"

def crawl_dunno_word(word, driver):
    # en-en
    soup_en = get_request(construct_dunno_search_url(word, "en"), driver=driver, wait_for_present=".item-content")

    # wait = WebDriverWait(driver, 10)
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, )))
    item_content_en = soup_en.select_one(".item-content")

    meaning_ele_en = item_content_en.select_one(".txt-mean")
    meaning_en = meaning_ele_en.get_text(strip=True, separator=' ') if meaning_ele_en else None
    definition = meaning_en

    pos_ele = soup_en.select_one(".box-content-title")
    part_of_speech = pos_ele.get_text(strip=True) if pos_ele else None

    # en-vi
    soup = get_request(construct_dunno_search_url(word, "vi"), driver=driver, wait_for_present=".item-content")
    # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".item-content")))
    item_content = soup.select_one(".item-content")

    meaning_ele = item_content.select_one(".txt-mean")
    meaning = meaning_ele.get_text(strip=True, separator=' ') if meaning_ele else None

    content_example_ele = item_content.select_one(".box-example .content-example")

    example_ele = content_example_ele.select_one(".txt-green")
    example = example_ele.get_text(strip=True, separator=' ') if example_ele else None

    example_meaning_ele = content_example_ele.select_one(".txt-green + app-word-search")
    example_meaning = example_meaning_ele.get_text(strip=True, separator=' ') if example_meaning_ele else None

    thumbnail_ele = soup.select_one(".kind-word-dark + img")
    thumbnail_url = thumbnail_ele["src"] if thumbnail_ele else None

    example_audio_url = get_audio_url(driver)

    print("Word:", word)
    print("Part of Speech:", part_of_speech)
    print("Meaning:", meaning)
    print("Example:", example)
    print("Example Meaning:", example_meaning)
    print("Example Audio URL:", example_audio_url)
    print("Definition:", definition)
    
    return {
        "word": word,
        "part_of_speech": part_of_speech,
        "meaning": meaning,
        "example": example,
        "example_meaning": example_meaning,
        "thumbnail_url": thumbnail_url,
        "example_audio_url": example_audio_url,
        "definition": definition
    }

if __name__ == "__main__":
    # Initialize the driver
    driver = init_driver()

    # Example word to search
    word = "hello"

    # Crawl dunno word
    result = crawl_dunno_word(word, driver)

    # Print the result
    print(result)

    # Quit the driver
    driver.quit()

