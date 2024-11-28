from extract_text import extract_text_from_pdf
from process_data_files import *

# sample data
file = "Data/HaiChau_Luan Ngu C4.pdf" 
text_dir = f'./extracted_text/'

if __name__ == "__main__":
    # extract_text_from_pdf(file, text_dir)
    
    # delete files that dont contain chinese text
    df = process_data_files(text_dir) # 2 columns: text, bbox
    # print(df.iloc[0]['bbox'])
    # print(df)
    # Save the processed dataframe to CSV
    csv_file = "processed_data.csv"
    df.to_csv(csv_file, index=False)
    print(f"Saved processed data to {csv_file}")

