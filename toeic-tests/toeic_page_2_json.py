from crawl_part1 import crawl_part1
from crawl_part2 import crawl_part2
from crawl_part3 import crawl_part3
from crawl_part4 import crawl_part4
from crawl_part5 import crawl_part5
from crawl_part6 import crawl_part6
from crawl_part7 import crawl_part7
import os

def toeic_page_2_json(folder_name, output_folder):
    folder_dir = 'text/' + folder_name
    output_folder = 'output_json/' + output_folder
    
    # Mk dir if not exist
    os.makedirs(output_folder, exist_ok=True)
    
    crawl_part1(folder_dir + '/part1.txt', output_folder + '/part1.json')
    crawl_part2(folder_dir + '/part2.txt', output_folder + '/part2.json')
    crawl_part3(folder_dir + '/part3.txt', output_folder + '/part3.json')
    crawl_part4(folder_dir + '/part4.txt', output_folder + '/part4.json')
    crawl_part5(folder_dir + '/part5.txt', output_folder + '/part5.json')
    crawl_part6(folder_dir + '/part6.txt', output_folder + '/part6.json')
    crawl_part7(folder_dir + '/part7.txt', output_folder + '/part7.json')
    
if __name__ == "__main__":
    toeic_page_2_json('2024_6', 'test_output/test1')
