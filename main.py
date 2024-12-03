from extract_text import extract_text_from_pdf
from process_data_files import *
from align_cn_vn_bboxes import *

# sample data
file = "Data/HaiChau_Luan Ngu C4.pdf" 
text_dir = f'./extracted_text/'
processed_data_json_file = "processed_data.json"

if __name__ == "__main__":
    # uncomment to extract text from pdf
    # --------------------------------

    # extract_text_from_pdf(file, text_dir)
    
    # # delete files that dont contain chinese text
    # processed_data = process_data_files(text_dir) # 2 columns: text, bbox

    # # Save the processed data to JSON
    # with open(processed_data_json_file, 'w', encoding='utf-8') as f:
    #     json.dump(processed_data, f, ensure_ascii=False, indent=4)
    # print(f"Saved processed data to {processed_data_json_file}")
    
    # --------------------------------


    # align bboxes
    print("Aligning bboxes...")
    aligned_df = align_cn_vn_bboxes(processed_data_json_file)
    print(aligned_df)
