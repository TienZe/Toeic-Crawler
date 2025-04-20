from crawler_utils import *


def get_word_of_lesson(lesson_path, driver):
    lesson_url = get_url(lesson_path)
    soup = get_request(lesson_url, driver, wait_for_presence="ol.wordlist")

    word_elements = soup.select("ol.wordlist a.word")
    words = []
    for word_ele in word_elements:
        word = word_ele.get_text(strip=True)
        words.append(word)
        
    return words

if __name__ == "__main__":
    # Initialize the driver
    driver = init_driver()

    # Example word to search
    path = "/lists/8105441"
    
    words = get_word_of_lesson(path, driver)
    
    for word in words:
        print(word)
    
    # Close the driver
    driver.quit()