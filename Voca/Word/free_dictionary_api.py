
import requests

api_dictionary_endpoint = "https://api.dictionaryapi.dev/api/v2/entries/en/"

def search_word(word):
    url = f"{api_dictionary_endpoint}{word}"
    response = requests.get(url)
    data = response.json()
    
    return data

def get_pronunciation(word):
    data = search_word(word)
    word_result = data[0]
    
    if "phonetic" in word_result:
        return word_result["phonetic"]
    elif "phonetics" in word_result:
        for phonetic_pair in word_result["phonetics"]:
            if "text" in phonetic_pair:
                return phonetic_pair["text"]

    return None
