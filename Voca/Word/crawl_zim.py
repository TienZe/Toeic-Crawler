from crawler_utils import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd

# Function to extract network requests from logs
def extract_network_calls(logs, pattern):
    for log in logs:
        try:
            log_data = json.loads(log["message"])["message"]
            
            # Filter for Network.requestWillBeSent events
            if log_data["method"] == "Network.requestWillBeSent":
                request_url = log_data["params"]["request"]["url"]
                
                # Filter for dunno audio media calls
                if pattern in request_url:
                    # print(f"Audio API call detected: {request_url}")
                    return request_url
        except Exception as e:
            return None
    return None
    

def get_audio_url(driver, get_example_audio=True):
    # Wait for the the audio button loaded
    wait = WebDriverWait(driver, 10)
    
    if get_example_audio:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box-audio")))
        
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".detail-word .box-word .txt-pronounce")))

    # Clear logs before interaction
    driver.get_log('performance')

    # Try different selectors to find audio button
    try:
        audio_element = None
        if get_example_audio:
            audio_element = driver.find_element(By.CSS_SELECTOR, ".box-audio")
            
        pronounce_element = driver.find_element(By.CSS_SELECTOR, ".detail-word .box-word .txt-pronounce")
        
        if audio_element:
            # Click the audio button
            audio_element.click()
            # print("Clicked audio button")
        
        if pronounce_element:
            pronounce_element.click()
            # print("Clicked pronounce button")
            
        # Wait a moment for the request to be sent
        time.sleep(0.3)
            
        logs = driver.get_log('performance')
        
        if get_example_audio:
            audio_url = extract_network_calls(logs, "https://data.dunno.ai/audios/example")
        else:
            audio_url = None

        pronounce_url = extract_network_calls(logs, "https://data.dunno.ai/audios/envi")
        
        return (audio_url, pronounce_url)
                
    except Exception as e:
        print(f"Error get audio url: {str(e)}")
        return None

def construct_zim_search_url(word):
    dunno_search_word_endpoint = "https://dictionary.zim.vn/anh-viet/"
    
    return f"{dunno_search_word_endpoint}/{word}"

def crawl_dunno_word(word, driver):
    # # en-en
    # soup_en = get_request(construct_dunno_search_url(word, "en"), driver=driver, wait_for_presence=".item-content")
    # item_content_en = soup_en.select_one(".item-content")

    # meaning_ele_en = item_content_en.select_one(".txt-mean")
    # meaning_en = meaning_ele_en.get_text(strip=True, separator=' ') if meaning_ele_en else None
    # definition = meaning_en

    # pos_ele = soup_en.select_one(".box-content-title")
    # part_of_speech = pos_ele.get_text(strip=True) if pos_ele else None

    # en-vi
    soup = get_request(construct_zim_search_url(word), driver=driver, wait_for_presence=".inline-block.w-full.text-primary.text-base-rps")
    
    return {
        "word": word,
    }
    item_content = soup.select_one(".item-content")

    meaning_ele = item_content.select_one(".txt-mean")
    meaning = meaning_ele.get_text(strip=True, separator=' ') if meaning_ele else None

    content_example_ele = item_content.select_one(".box-example .content-example")

    example = None
    example_meaning = None
    
    if content_example_ele:
        example_ele = content_example_ele.select_one(".txt-green")
        example = example_ele.get_text(strip=True, separator=' ') if example_ele else None

        example_meaning_ele = content_example_ele.select_one(".txt-green + app-word-search")
        example_meaning = example_meaning_ele.get_text(strip=True, separator=' ') if example_meaning_ele else None
    # else:
    #     example_ele = soup.select_one(".box-example .content-example .txt-green")
    #     example = example_ele.get_text(strip=True, separator=' ') if example_ele else None
        
    #     example_meaning_ele = example_ele.find_next("app-word-search")
    #     example_meaning = example_meaning_ele.get_text(strip=True, separator=' ') if example_meaning_ele else None

    thumbnail_ele = soup.select_one(".kind-word-dark + img")
    thumbnail_url = thumbnail_ele["src"] if thumbnail_ele else None
    
    pronounce_ele = soup.select_one(".detail-word .box-word .txt-pronounce")
    pronunciation = pronounce_ele.get_text(strip=True) if pronounce_ele else None

    example_audio_url, pronunciation_url = get_audio_url(driver, get_example_audio=(example is not None))

    # print("Word:", word)
    # print("Pronunciation:", pronunciation)
    # print("Pronounce_url:", pronunciation_url)
    # print("Part of Speech:", part_of_speech)
    # print("Meaning:", meaning)
    # print("Example:", example)
    # print("Example Meaning:", example_meaning)
    # print("Example Audio URL:", example_audio_url)
    # print("Definition:", definition)
    
    return {
        "word": word,
        "pronunciation": pronunciation,
        "pronunciation_audio": pronunciation_url,
        "part_of_speech": part_of_speech,
        "meaning": meaning,
        "example": example,
        "example_meaning": example_meaning,
        "thumbnail": thumbnail_url,
        "example_audio": example_audio_url,
        "definition": definition
    }
    
def get_and_save_word_info(chunk, output_path, chunk_index):
    driver = init_driver()
    result = []
    
    len_chunk = len(chunk)
    
    for index in range(len_chunk):
        word = chunk.iloc[index]["Word"]
        print(f"Processing word chunk {chunk_index} - {index + 1}/{len_chunk}: {word}")
        
        try:
            result.append(crawl_dunno_word(word, driver))
        except Exception as e:
            print(f"Error with word {word}")
            # raise e
            
    df = pd.DataFrame(result)
    df.to_csv(output_path, index=False)
    print(f"Saved chunk to {output_path}")
    driver.quit()

if __name__ == "__main__":
    # Initialize the driver
    driver = init_driver()
    
    # Example word to search
    word = "admonition"

    # Crawl dunno word
    result = crawl_dunno_word(word, driver)

    # Print the result
    print(result)

    # Quit the driver
    driver.quit()

