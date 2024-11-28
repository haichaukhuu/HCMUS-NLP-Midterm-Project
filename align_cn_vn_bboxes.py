import numpy as np
import pandas as pd
from pathlib import Path

# text,bbox,page_num,lang

def min_distance(bbox1, bbox2):
    """
    Calculate min Euclidean distance between two bounding boxes using numpy
    """
    # Get centers of bboxes
    center1 = np.array([(bbox1[0] + bbox1[2])/2, (bbox1[1] + bbox1[3])/2])
    center2 = np.array([(bbox2[0] + bbox2[2])/2, (bbox2[1] + bbox2[3])/2])
    
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


# def align_cn_viet_bboxes(csv_file: str) -> pd.DataFrame:
#     """
#     Align Chinese and Vietnamese bboxes, page by page
#     """
#     df = pd.read_csv(csv_file)

    

# test
df = pd.read_csv('processed_data.csv')
cn,vn = get_words_by_page(df, 1)
print(f"Chinese words:\n{cn}")
print(len(cn))
print(f"Vietnamese words:\n{vn}")
print(len(vn))