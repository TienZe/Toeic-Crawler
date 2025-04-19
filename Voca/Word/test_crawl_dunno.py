from crawler_utils import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json

# Enable performance logging in Chrome
chrome_options = uc.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})

# Initialize driver with performance logging
driver = uc.Chrome(options=chrome_options)
driver.set_page_load_timeout(20)

url = "https://dunno.ai/search/word/combination?hl=vi"
driver.get(url)

# Wait for the the audio button loaded
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".box-audio")))

# Function to extract network requests from logs
def extract_network_calls(logs):
    for log in logs:
        try:
            log_data = json.loads(log["message"])["message"]
            
            # Filter for Network.requestWillBeSent events
            if log_data["method"] == "Network.requestWillBeSent":
                request_url = log_data["params"]["request"]["url"]
                # Filter for audio-related requests
                if "https://data.dunno.ai/audios/example" in request_url:
                    print(f"Audio API call detected: {request_url}")
                    return request_url
        except Exception as e:
            pass
    return None

# Clear logs before interaction
driver.get_log('performance')

# Try different selectors to find audio button
try:
    # Try to find an audio-related element using multiple selectors
    selector = ".box-audio"
    
    audio_element = None
    
    elements = driver.find_elements(By.CSS_SELECTOR, selector)
    if elements:
        print(f"Found audio element with selector: {selector}")
        audio_element = elements[0]
    
    if audio_element:
        # Click the audio button
        audio_element.click()
        print("Clicked audio button")
        
        # Wait a moment for the request to be sent
        time.sleep(3)
        
        # Get performance logs
        logs = driver.get_log('performance')
        audio_url = extract_network_calls(logs)
        
        if audio_url:
            print(f"\nCaptured audio API call: {audio_url}")
            
except Exception as e:
    print(f"Error: {str(e)}")

# Quit the driver
driver.quit()

