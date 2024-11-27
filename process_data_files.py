import json
from pathlib import Path
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
    # Convert to string representation for opening the file
    with open(str(json_file), "r", encoding="utf-8-sig") as f:
        data = json.load(f)
        for item in data:
            if len(item["text"]) == 1 and is_chinese_char(item["text"]):
                return True
    return False

def delete_file_if_no_chinese(file_path):
    '''
    Delete a file if it does not contain chinese characters
    '''
    if not has_chinese(file_path):
        print(f"Deleting {file_path.name} because it does not contain chinese characters")
        # os.remove(file_path)

def process_data_files(data_dir):
    '''
    Process all data files in a directory
    '''
    # Convert input to Path object and resolve to absolute path
    data_path = Path(data_dir).resolve()
    
    # Get all JSON files sorted by page number
    json_files = sorted(
        data_path.glob('*.json'), 
        key=lambda x: int(x.stem.split('_')[1])
    )
    
    for file_path in json_files:
        delete_file_if_no_chinese(file_path)


