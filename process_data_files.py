import json
import os
'''
Functions for processing chinese-vietnamese text files will be written here.
The processing includes:
- Checking if a text file contains chinese characters
- Deleting a text file if it does not contain chinese characters

'''

def is_chinese_char(char):
    '''
    Check if a character is a Chinese character
    '''
   
    # Unicode ranges for Chinese characters
    ranges = [
        (0x4E00, 0x9FFF),   # CJK Unified Ideographs
        (0x3400, 0x4DBF),   # CJK Unified Ideographs Extension A
        (0x20000, 0x2A6DF), # CJK Unified Ideographs Extension B
        (0x2A700, 0x2B73F), # CJK Unified Ideographs Extension C
        (0x2B740, 0x2B81F), # CJK Unified Ideographs Extension D
        (0x2B820, 0x2CEAF), # CJK Unified Ideographs Extension E
        (0xF900, 0xFAFF),   # CJK Compatibility Ideographs
    ]
    
    code = ord(char)
    return any(start <= code <= end for start, end in ranges)

def has_chinese(json_file):
    '''
    Check if a json file contains chinese characters
    '''
    with open(json_file, "r", encoding = "utf-8-sig") as json_file:
        data = json.load(json_file)
        for item in data:
            if len(item["text"]) == 1 and is_chinese_char(item["text"]):
                return True
    return False

def delete_file_if_no_chinese(file_path):
    '''
    Delete a file if it does not contain chinese characters
    '''
    if not has_chinese(file_path):
        print(f"Deleting {file_path} because it does not contain chinese characters")
        os.remove(file_path)

def process_data_files(data_dir):
    '''
    Process all data files in a directory
    '''
    for file in os.listdir(data_dir):
        file_path = os.path.join(data_dir, file)
        delete_file_if_no_chinese(file_path)


