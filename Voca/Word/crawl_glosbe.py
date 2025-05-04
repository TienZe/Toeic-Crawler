from crawler_utils import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import json
import pandas as pd

def construct_url(word):
    dunno_search_word_endpoint = "https://glosbe.com/en/vi"
    
    return f"{dunno_search_word_endpoint}/{word}"

def crawl_glosbe_word(word, driver):
    wait = WebDriverWait(driver, 6)
    get_request(construct_url(word), driver=driver, wait_for_presence="#dictionary-content", to_soup=False)
    
    sleep(3)
    
    # Do first first interaction on the page to trigger other event handler in the page
    driver.find_element(By.CSS_SELECTOR, "#phraseDetails_activator-0").click()
    
    # Open the translation element
    for translation_ele_by_driver in driver.find_elements(By.CSS_SELECTOR, 'li[data-element="translation"] .fragment_expandIcon + .flex-1'):
        # translation_ele_by_driver.click()
        ActionChains(driver).click(translation_ele_by_driver).perform()
        # print("Clicking translation element")
    
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".translation__example")))
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[data-element="translation"]')))
    except Exception as e:
        print(f"Error waiting for translation example of word {word}")

    # refresh soup
    soup = page_source_2_soup(driver.page_source)

    word_summary = soup.select_one("#phraseDetails_activator-0")
    
    
    if not word_summary:
        return None
    
    word_type_eles = word_summary.select(".text-xxs.text-gray-500.inline-block span")
    main_word_types = []
    for word_type_ele in word_type_eles:
        word_type_ = word_type_ele.get_text(strip=True)
        if word_type_:
            main_word_types.append(word_type_)
        
    
    definition = None
    definition_ele = word_summary.select_one('#phraseDetails_container-0 p')
    
    if definition_ele:
        if definition_ele.span:
            definition_ele.span.decompose()

        definition = definition_ele.get_text(strip=True)
    
    
    translation_eles = soup.select('li[data-element="translation"]')
    
    translation = []
    
    for translation_ele in translation_eles:
        wrap_ele = translation_ele.select_one(".flex-1 div.leading-10")
        if not wrap_ele:
            continue
        
        meaning_ele = wrap_ele.select_one("h3")
        respective_word_type_ele = wrap_ele.select_one(".dir-aware-pr-1")
        
        example_wrap_ele = translation_ele.select_one(".translation__example")
        
        example_ = None
        example_meaning_ = None
        
        if example_wrap_ele:
            # select direct child
            p_tag = example_wrap_ele.find_all(["p", "div"], recursive=False)
            # p_tag = example_wrap_ele.select('[class*="dir-aware"]')
            if len(p_tag) > 0:
                example_ = p_tag[0].get_text(strip=True, separator=' ')
                example_meaning_ = p_tag[1].get_text(strip=True, separator=' ') if len(p_tag) > 1 else None
            
        # print("Translation Block--")
        # print("Find meaning", meaning_ele.get_text(strip=True) if meaning_ele else None)
        # print("Find word type", respective_word_type_ele.get_text(strip=True) if respective_word_type_ele else None)
        # print("Find example", example_)
        # print("Find example meaning", example_meaning_)
        
        translation.append({
            "meaning": meaning_ele.get_text(strip=True) if meaning_ele else None,
            "word_type": respective_word_type_ele.get_text(strip=True) if respective_word_type_ele else None,
            "example": example_,
            "example_meaning": example_meaning_,
        })
        
    selected_translation = None
    
    for word_type in main_word_types:
        for translation_ in translation:
            if word_type == translation_["word_type"] or translation_["word_type"] is None:
                if not selected_translation:
                    selected_translation = translation_
                elif not selected_translation["example"] and translation_["example"]:
                    selected_translation = translation_
    
    if not selected_translation and len(translation) > 0: # no word type match
      selected_translation = translation[0]
      
    meaning = None
    part_of_speech = None
    example = None
    example_meaning = None
                    
    if selected_translation:
        meaning = selected_translation["meaning"]
        part_of_speech = selected_translation["word_type"] 
        example = selected_translation["example"]
        example_meaning = selected_translation["example_meaning"]
        
    if not part_of_speech:
        part_of_speech = main_word_types[0] if len(main_word_types) > 0 else None
        
    if not meaning:
        glosbe_translate_ele = None
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#glosbeTranslate_container a")))
            glosbe_translate_ele = soup.select_one("#glosbeTranslate_container a")
        except Exception as e:
            print(f"Not found glosbe meaning for word {word}")

        
        if glosbe_translate_ele:
            meaning = glosbe_translate_ele.get_text(strip=True)
        else:
            gg_translate_ele = None
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#googleTranslate_container")))
                gg_translate_ele = soup.select_one("#googleTranslate_container")

            except Exception as e:
                print(f"Not found google meaning for word {word}")
            
            if gg_translate_ele:
                meaning = gg_translate_ele.get_text(strip=True)
                
    if not example:
        example_sections = soup.select("#examples #tmem_first_examples .odd\:bg-slate-100")
        
        examples = []
        
        for example_section in example_sections:
            example_eles = example_section.select(".w-1\/2")

            if len(example_eles) == 2:
                example_ = example_eles[0].get_text(strip=True, separator=' ')
                example_meaning_ = example_eles[1].get_text(strip=True, separator=' ')
                examples.append({
                    "example": example_,
                    "example_meaning": example_meaning_
                })
                
        # select the example with minimum length
        if len(examples) > 0:
            min_example = min(examples, key=lambda x: len(x["example"]))
            example = min_example["example"]
            example_meaning = min_example["example_meaning"]
    
    # print("Word:", word)
    # # print("Pronunciation:", pronunciation)
    # # print("Pronounce_url:", pronunciation_url)
    # print("Part of Speech:", part_of_speech)
    # print("Meaning:", meaning)
    # print("Example:", example)
    # print("Example Meaning:", example_meaning)
    # # print("Example Audio URL:", example_audio_url)
    # print("Definition:", definition)
    
    return {
        "word": word,
        # "pronunciation": pronunciation,
        # "pronunciation_audio": pronunciation_url,
        "part_of_speech": part_of_speech,
        "meaning": meaning,
        "example": example,
        "example_meaning": example_meaning,
        # "thumbnail": thumbnail_url,
        # "example_audio": example_audio_url,
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
            result.append(crawl_glosbe_word(word, driver))
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
    word = "undersized"
    
    # Crawl dunno word
    result = crawl_glosbe_word(word, driver)

    # Print the result
    print(result)

    # Quit the driver
    driver.quit()

