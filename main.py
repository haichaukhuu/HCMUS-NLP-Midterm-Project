from extract_text import extract_text_from_pdf
from process_data_files import *
from align_cn_vn_bboxes import *

# sample data
file = "Data/HaiChau_Luan Ngu C4.pdf" 
text_dir = f'./extracted_text/'
csv_file = "processed_data.csv"

if __name__ == "__main__":
    # extract_text_from_pdf(file, text_dir)
    
    # delete files that dont contain chinese text
    # df = process_data_files(text_dir) # 2 columns: text, bbox

    # Save the processed dataframe to CSV
    # df.to_csv(csv_file, index=False)
    # print(f"Saved processed data to {csv_file}")

    # align bboxes
    print("Aligning bboxes...")
    aligned_df = align_cn_vn_bboxes(csv_file)
    print(aligned_df)
