import os
import re
import json
from datetime import datetime
import demjson3

#=========== CONFIG ============
# Directory containing part*.js files
PARTS_DIR = os.path.join(os.path.dirname(__file__), 'output_json/2023/test1')
PART_FILES = [f'part{i}.js' for i in range(1, 8)]

# Output directory for SQL
OUTPUT_SQL_DIR = os.path.join(os.path.dirname(__file__), 'output_sql/2023/test1')
OUTPUT_SQL_FILE = os.path.join(OUTPUT_SQL_DIR, 'export.sql')

# Set the test name here (or prompt if needed)
TEST_ID = 3 # Start id for toeic_tests
TEST_NAME = 'Practice Set 2023 TOEIC Test 1'

#=========== END CONFIG ============
def parse_js_array(js_path):
    with open(js_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    # Remove trailing semicolon if present
    if content.endswith(';'):
        content = content[:-1]
    # demjson3 can parse JS-style objects/arrays directly!
    return demjson3.decode(content)

def sql_escape(val):
    if val is None:
        return 'NULL'
    if isinstance(val, str):
        return "'" + val.replace("'", "''") + "'"
    return str(val)

def main():
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    sql = []

    # 1. toeic_tests
    sql.append(f"INSERT INTO toeic_tests (id, name, description, created_at, updated_at) VALUES ({TEST_ID}, {sql_escape(TEST_NAME)}, NULL, '{now}', '{now}');")

    # 2. Each test has 103 question groups
    group_id = (TEST_ID -1) * 103 + 1 # Start id for question_groups
    global_group_index = 0
    

    for part_num, part_file in enumerate(PART_FILES, 1):
        part_path = os.path.join(PARTS_DIR, part_file)
        if not os.path.exists(part_path):
            continue
        groups = parse_js_array(part_path)
        
        
        for group in groups:
            transcript = group.get('transcript')
            passage = group.get('detail') if 'detail' in group else None
            sql.append(f"INSERT INTO question_groups (id, part, group_index, transcript, passage, toeic_test_id, created_at, updated_at) VALUES ("
                       f"{group_id}, {sql_escape(str("part" + str(part_num)))}, {global_group_index}, {sql_escape(transcript)}, {sql_escape(passage)}, {TEST_ID}, '{now}', '{now}');")
            global_group_index += 1
            # Medias: audioUrl
            if group.get('audioUrl'):
                sql.append(f"INSERT INTO question_medias (file_url, file_public_id, file_type, `order`, question_group_id, created_at, updated_at) VALUES ("
                           f"{sql_escape(group['audioUrl'])}, NULL, 'audio', NULL, {group_id}, '{now}', '{now}');")
            # Medias: images
            for img in group.get('image', []):
                file_url = img.get('fileUrl')
                idx = img.get('index', 0)
                sql.append(f"INSERT INTO question_medias (file_url, file_public_id, file_type, `order`, question_group_id, created_at, updated_at) VALUES ("
                           f"{sql_escape(file_url)}, NULL, 'image', {idx}, {group_id}, '{now}', '{now}');")

            # Questions
            for q in group['questionData']:
                qtext = q.get('question', '')
                qnum = q.get('questionNumber', 0)
                explain = q.get('explain')
                answers = q.get('answer', [])
                correct = q.get('correctAnswer')
                # Map answers to A/B/C/D
                A = sql_escape(answers[0]) if len(answers) > 0 else 'NULL'
                B = sql_escape(answers[1]) if len(answers) > 1 else 'NULL'
                C = sql_escape(answers[2]) if len(answers) > 2 else 'NULL'
                D = sql_escape(answers[3]) if len(answers) > 3 else 'NULL'
                # Map correct answer to A/B/C/D if possible
                correct_letter = 'NULL'
                if correct:
                    for idx, opt in enumerate(['A', 'B', 'C', 'D']):
                        if len(answers) > idx and (correct.strip() == answers[idx]):
                            correct_letter = f"'{opt}'"
                            break
                    # If not found, try to match by value
                    if correct_letter == 'NULL' and correct in answers:
                        correct_letter = f"'{chr(65 + answers.index(correct))}'"
                sql.append(f"INSERT INTO questions (question, question_number, explanation, A, B, C, D, correct_answer, question_group_id, created_at, updated_at) VALUES ("
                           f"{sql_escape(qtext)}, {qnum}, {sql_escape(explain)}, {A}, {B}, {C}, {D}, {correct_letter}, {group_id}, '{now}', '{now}');")
            group_id += 1

    # Ensure output directory exists
    os.makedirs(OUTPUT_SQL_DIR, exist_ok=True)
    with open(OUTPUT_SQL_FILE, 'w', encoding='utf-8') as f:
        f.write('SET NAMES utf8mb4;\n')
        f.write('\n'.join(sql))
    print(f"SQL export written to: {OUTPUT_SQL_FILE}")

if __name__ == '__main__':
    main()
