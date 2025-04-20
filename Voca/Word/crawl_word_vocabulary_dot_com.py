from crawler_utils import *
import pandas as pd

def get_word_of_lesson(lesson_path, driver):
    lesson_url = get_url(lesson_path)
    soup = get_request(lesson_url, driver, wait_for_presence="ol.wordlist")

    word_elements = soup.select("ol.wordlist a.word")
    words = []
    for word_ele in word_elements:
        word = word_ele.get_text(strip=True)
        words.append(word)
        
    return words

def get_and_save_words_of_lesson(lesson_chunk, output_path):
    words = []
    driver = init_driver()
    
    for i in range(len(lesson_chunk)):
        lesson = lesson_chunk.iloc[i]
        lesson_id = lesson['Lesson ID']
        lesson_path = lesson['Lesson Link']
        lesson_name = lesson['Lesson Name']
        print(f'Getting words of {lesson_name} ({lesson_id})')
        
        try:
            words_of_lesson = get_word_of_lesson(lesson_path, driver=driver)
            for word in words_of_lesson:
                words.append({
                    'Word': word,
                    'Lesson ID': lesson_id,
                })
        except Exception as e:
            print(f'Error: {e}')

    words_df = pd.DataFrame(words)
    words_df.to_csv(output_path, index=False)
    driver.quit()
    

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