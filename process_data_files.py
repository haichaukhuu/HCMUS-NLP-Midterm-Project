import json
from pathlib import Path
import os
import pandas as pd
from copy import deepcopy
from align_cn_viet_bboxes import *
import numpy as np


'''
Functions for processing chinese-vietnamese datafiles will be written here.
The processing includes:
- Checking if a file contains chinese characters
- Deleting a file if it does not contain chinese characters
- Looping through all files, processing them, and combining them into a single dataframe
    + Removing all non-chinese and non-vietnamese characters
    + Stripping whitespace from text
    + Adding a page number column
    + Adding a language column, classifying the text into chinese, vietnamese
    + Aligning the chinese char with corresponding vietnamese char
- Returning the cleaned dataframe with 3 columns: text, bbox, page_num, lang
- Saving the dataframe to a csv file
'''

def is_chinese_char(char):
    '''
    Check if a character is a Chinese character
    '''
    if len(char) != 1:
        return False
   
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

def is_viet_text(text):
    '''
    Check if a text is in Vietnamese
    '''
    vietnamese_chars = "aáàảãạăắằẳẵặâấầẩẫậbcdeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvwxyỳỷỹỵ"
    return any(char in text for char in vietnamese_chars)

def delete_file_if_no_chinese(file_path):
    '''
    Delete a file if it does not contain chinese characters
    '''
    if not has_chinese(file_path):
        print(f"Deleting {file_path.name} because it does not contain chinese characters")
        file_path.unlink()


def parse_bbox_coords(bbox: list) -> np.ndarray:
    return np.array(list(map(float, bbox)))


# -----------------%%%%%%%%-----------------
# Main processing function
# -----------------%%%%%%%%-----------------

def process_data_files(data_dir) -> pd.DataFrame:
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

    # Get updated list of JSON files after deletions
    json_files = sorted(
        data_path.glob('*.json'),
        key=lambda x: int(x.stem.split('_')[1])
    )

    # Read each JSON file into a dataframe
    all_files_df = pd.DataFrame()

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)
            df = pd.DataFrame(data)

            page_num = int(json_file.stem.split('_')[1])
            df['page_num'] = page_num + 1 # Page number starts from 1

            # Parse bbox coordinates to numpy array
            df['bbox'] = df['bbox'].apply(parse_bbox_coords)

            # Process each row's text
            # Remove non-chinese and non-vietnamese characters
            for index, row in df.iterrows():
                if not is_chinese_char(row['text']) and not is_viet_text(row['text']):
                    df.drop(index, inplace=True)
                else:
                    df.at[index, 'text'] = row['text'].strip()
                    # Determine language for each row
                    if is_chinese_char(row['text']):
                        df.at[index, 'lang'] = 'cn'
                    elif is_viet_text(row['text']):
                        df.at[index, 'lang'] = 'vn' 
                    else:
                        df.at[index, 'lang'] = 'other'

            all_files_df = pd.concat([all_files_df, df], ignore_index=True)

    return all_files_df


