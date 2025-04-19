from crawler_utils import get_url, get_request, init_driver
import pandas as pd
from html import unescape
from bs4 import BeautifulSoup
import time 
import undetected_chromedriver as uc

def get_lessons_of_collection(collection, driver):
    collection_id = collection['ID']
    collection_path = collection['Link']
    print(f"Get lessons of collection ID: {collection_id}")
    
    # Get the lessons page
    collection_url = get_url(collection_path)
    soup = get_request(collection_url, driver, wait=5)
    
    # Extract lesson dom
    lesson_doms = soup.select(".wordlist")
    
    lessons = []
    for lesson_dom in lesson_doms:
        a_ele = lesson_dom.select_one(".header h2 a")
        
        if not a_ele:
            continue
        
        # Extract lesson name and link
        lesson_name = a_ele.contents[0].strip()
        # Clean HTML entities and special characters
        lesson_name = unescape(lesson_name).replace('\ufeff', '')
        
        lesson_link = a_ele['href']
        
        if lesson_name and lesson_link:
            lessons.append({
                'Lesson Name': lesson_name,
                'Lesson Link': lesson_link,
                'Collection ID': int(collection_id)
            })
    
    return lessons


def get_lessons_of_collection_chunk(chunk, output_path):
    driver = init_driver()
    result = []
    
    for i in range(len(chunk)):
        collection = chunk.iloc[i]
        lessons = get_lessons_of_collection(collection, driver)
        result = result + lessons
        
    result_df = pd.DataFrame(result)
    result_df.to_csv(output_path, index=False)
    driver.quit()
    return result_df