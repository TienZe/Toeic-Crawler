
from crawler_utils import *
import pandas as pd
from free_dictionary_api import get_pronunciation as get_pronunciation_from_api

base_url = "https://www.vocabulary.com/dictionary/"


def get_dictionary_url(word):
    return f"{base_url}{word}"

def get_pronunciation(word, driver):
    url = get_dictionary_url(word)
    
    soup = get_request(url, driver, wait_for_presence=".ipa-section")
    
    pronunciation_section = soup.select_one(".ipa-section")
    
    pronunciation_elements = pronunciation_section.select(".span-replace-h3")
    
    pronunciation = ""
    for pronunciation_element in pronunciation_elements:
        pronunciation = pronunciation_element.get_text(strip=True)
    
    return pronunciation


def get_and_save_pronunciation_by_chunk_df(chunk_df, output_path, chunk_index=None):
    driver = init_driver()
    
    words = []
    length = len(chunk_df)
    
    for index, row in chunk_df.iterrows():
        word = row['word']
        
        pronunciation = None

        try:
            pronunciation = get_pronunciation(word, driver)
        except Exception as e:
            print(f"Error getting pronunciation for {word}, error:{e}")
                
        if not pronunciation:
            print(f"Try to get pronunciation for {word} from dictionary api")
            try:
                pronunciation = get_pronunciation_from_api(word)
                sleep(2)
            except Exception as e:
                print(f"Error getting pronunciation for {word} from dictionary api, error: {e}")
            
        words.append({
            'word': word,
            'pronunciation': pronunciation
        })
        
        if index % 50 == 0:
            print(f"Processed {index + 1} / {length} words of chunk {chunk_index}")
        
    words_df = pd.DataFrame(words)
    words_df.to_csv(output_path, index=False)
    driver.quit()

if __name__ == "__main__":
    # driver = init_driver()
    
    word = "reactionary"
    # pronunciation = get_pronunciation(word, driver)
    pronunciation = get_pronunciation_from_api(word)
    print(pronunciation)
