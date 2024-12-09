import json
from pathlib import Path
import os
import pandas as pd
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

# example of a bbox
    # {
    #     "text": "四",
    #     "bbox": [
    #         [
    #             125.9000015258789,
    #             85.782470703125
    #         ],
    #         [
    #             197.89999389648438,
    #             85.782470703125
    #         ],
    #         [
    #             197.89999389648438,
    #             133.782470703125
    #         ],
    #         [
    #             125.9000015258789,
    #             133.782470703125
    #         ]
    #     ]
    # },
def parse_bbox_coords(bbox: list) -> np.ndarray:
    return np.array([(float(point[0]), float(point[1])) for point in bbox], dtype=float)

# test
# page_0_file = "extracted_text/page_0.json"
# with open(page_0_file, 'r', encoding='utf-8-sig') as f:
#     data = json.load(f)
#     for item in data:
#         if item['text'] == '四':
#             bbox = item['bbox']
#             print(f"BBox for '四' in page 0: {bbox}")
#             print(f"Parsed bbox: {parse_bbox_coords(bbox)}")
#             print(f"Dtype: {parse_bbox_coords(bbox).dtype}")

#             break




# -----------------%%%%%%%%-----------------
# Main processing function
# -----------------%%%%%%%%-----------------

def process_data_files(data_dir):
    '''
    Process all data files in a directory and return a dictionary
    '''
    data_path = Path(data_dir).resolve()
    
    json_files = sorted(
        data_path.glob('*.json'), 
        key=lambda x: int(x.stem.split('_')[1])
    )
    
    for file_path in json_files:
        delete_file_if_no_chinese(file_path)

    json_files = sorted(
        data_path.glob('*.json'),
        key=lambda x: int(x.stem.split('_')[1])
    )

    all_files_data = []

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8-sig') as f:
            data = json.load(f)

            page_num = int(json_file.stem.split('_')[1])
            for item in data:
                item['page_num'] = page_num

                item['bbox'] = parse_bbox_coords(item['bbox']).tolist()

                if is_chinese_char(item['text']) or is_viet_text(item['text']):
                    item['text'] = item['text'].strip()
                    if is_chinese_char(item['text']):
                        item['lang'] = 'cn'
                    elif is_viet_text(item['text']):
                        item['lang'] = 'vn'
                    else:
                        item['lang'] = 'other'
                    all_files_data.append(item)

    return all_files_data


