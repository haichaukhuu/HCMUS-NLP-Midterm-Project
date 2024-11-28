import numpy as np
import pandas as pd
from pathlib import Path
import ast  # Add this import at the top

# text,bbox,page_num,lang

def get_center(bbox) -> np.ndarray:
    # safely convert string representation to array
    if isinstance(bbox, str):
        # Clean the string and convert to list before making numpy array
        cleaned_bbox = bbox.strip('[]').replace('  ', ' ').split()
        bbox = np.array([float(x) for x in cleaned_bbox])
    elif not isinstance(bbox, np.ndarray):
        bbox = np.array(bbox)
    
    return np.array([(bbox[0] + bbox[2])/2, (bbox[1] + bbox[3])/2])  # x,y

def min_distance(bbox1, bbox2):
    """
    Calculate min Euclidean distance between two bounding boxes using numpy
    """
    # Get centers of bboxes
    center1 = get_center(bbox1)
    center2 = get_center(bbox2)
    
    # Calculate Euclidean distance between centers using numpy
    return np.linalg.norm(center1 - center2)


def get_words_by_page(df: pd.DataFrame, page_num: int) -> tuple[list, list]:
    """
    Extract Chinese and Vietnamese words with their bboxes by page
    Returns two lists of tuples containing (word, bbox) pairs
    """
    page_df = df[df['page_num'] == page_num]
    cn_words = []
    vn_words = []
    
    # Process one page
    # Extract Chinese words and bboxes
    all_cn = page_df[page_df['lang'] == 'cn']
    cn_words.extend(list(zip(all_cn['text'], all_cn['bbox'])))
        
    # Extract Vietnamese words and bboxes
    all_vn = page_df[page_df['lang'] == 'vn']
    vn_words.extend(list(zip(all_vn['text'], all_vn['bbox'])))
        
    return cn_words, vn_words



def align_words(page_num: int, cn_words: list, vn_words: list) -> list:
    """
    Align Chinese and Vietnamese words based on vertical alignment.
    Vietnamese bbox should be below Chinese bbox and be its translation.
    
    Rules for alignment:
    1. Vietnamese word must be vertically below Chinese word (same column)
    2. Vietnamese word must be the closest word below the Chinese word
    3. Vietnamese word must be the translation of the Chinese word
                
    Returns list of dicts containing aligned word pairs with their bboxes
    Example return format for aligned words:
    [
        {
            'text_cn': '四',
            'text_vi': 'Tứ', 
            'bbox_cn': [125.9, 85.78, 197.89, 133.78],
            'bbox_vi': [141.97, 134.32, 161.11, 148.36]
        },
        {
            'text_cn': '書',
            'text_vi': 'Thư',
            'bbox_cn': [125.9, 156.22, 197.89, 204.22], 
            'bbox_vi': [138.25, 215.44, 164.95, 229.48]
        }
    ]
    """
    aligned = []
            
    # For each Chinese word, find the closest Vietnamese word below it
    for cn_word, cn_bbox in cn_words:
        min_dist = float('inf')
        best_match = None
        
        cn_center = get_center(cn_bbox)
        cn_center_x = cn_center[0]

        # Loop through each Vietnamese word
        for vn_word, vn_bbox in vn_words:                
            vn_center = get_center(vn_bbox)
            vn_center_x = vn_center[0]

            # Check if words are vertically aligned (same column)
            # Allow small horizontal deviation (e.g. within 20 pixels)
            x_deviation = abs(cn_center_x - vn_center_x)
            
            # x1,y1,x2,y2
            # Vietnamese word must be below Chinese word
            # (since y-coordinates increase going down)
            if (vn_bbox[1] > cn_bbox[3]) and (x_deviation < 25):
                dist = min_distance(cn_bbox, vn_bbox)
                if dist < min_dist:
                    min_dist = dist
                    best_match = (vn_word, vn_bbox)
        
        # Add aligned pair if match found
        if best_match is not None:
            aligned.append({
                'page_num': page_num,
                'text_cn': cn_word,
                'text_vi': best_match[0],
                'bbox_cn': cn_bbox,
                'bbox_vi': best_match[1]
            })
                    
    return aligned

def align_cn_vn_bboxes(csv_file: str) -> pd.DataFrame:
    """
    Align Chinese and Vietnamese bboxes, page by page
    Returns a dataframe with aligned bboxes, including below columns:
    - page_num
    - text_cn
    - text_vi
    - bbox_cn
    - bbox_vi
    """
    df = pd.read_csv(csv_file)
    page_nums = df['page_num'].unique()
    aligned_df = pd.DataFrame(columns=['page_num', 'text_cn', 'text_vi', 'bbox_cn', 'bbox_vi'])

    for page_num in page_nums:
        cn_words, vn_words = get_words_by_page(df, page_num)
        words_aligned = align_words(page_num, cn_words, vn_words) #list of dicts
        # aligned_df = aligned_df.append(words_aligned, ignore_index=True)
        
        aligned_df = pd.concat([aligned_df, pd.DataFrame(words_aligned)], ignore_index=True)

    return aligned_df


# # test
# df = pd.read_csv('processed_data.csv')
# cn,vn = get_words_by_page(df, 1)
# print(f"Chinese words:\n{cn}")
# print(len(cn))
# print(f"Vietnamese words:\n{vn}")
# print(len(vn))