import re
import os
import numpy as np
import pandas as pd
import fitz
import json
import shutil
from openpyxl import load_workbook

# Configure pandas display settings
pd.set_option("display.max_colwidth", None)  # Display full content without truncation
pd.set_option("display.max_columns", None)   # Show all columns
pd.set_option("display.width", 1000)         # Set wide display width
pd.set_option('display.max_rows', None)      # Show all rows
pd.options.display.float_format = '{:.2f}'.format

def extract_pdf_content(pdf_path, output_dir):
    document = fitz.open(pdf_path)
    
    # Create directories for text and images
    text_output_dir = os.path.join(output_dir, "text")
    images_output_dir = os.path.join(output_dir, "images")
    
    os.makedirs(text_output_dir, exist_ok=True)
    os.makedirs(images_output_dir, exist_ok=True)

    # Process each page
    for page_number in range(len(document)):
        print(f"Processing page {page_number}")
        
        # Extract content and bounding boxes
        page = document[page_number]
        dict_elements = page.get_text('dict')
        text_data = []
        
        for block in dict_elements['blocks']:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    text = span['text'].strip()
                    if text == '':
                        continue
                    text_data.append({
                        'text': text,
                        'bbox': span['bbox'],
                        'size': span['size']
                    })
        
        # Save text content and bounding boxes to JSON
        page_text_file = os.path.join(text_output_dir, f"HaiChau_Luan Ngu C4_page{page_number:03}.json")
        with open(page_text_file, 'w', encoding='utf-8-sig') as f:
            json.dump(text_data, f, ensure_ascii=False, indent=4)

        print(f"Extracted text for page {page_number}")
        
        # Extract and save page image
        pixmap = page.get_pixmap(dpi=72)  # Set DPI=72 to match bbox coordinates
        page_image_file = os.path.join(images_output_dir, f"HaiChau_Luan Ngu C4_page{page_number:03}.png")
        pixmap.save(page_image_file)
        
        print(f"Saved image for page {page_number}")

    document.close()

def create_dataframe(filename):
    with open(filename, 'r', encoding='utf-8-sig') as file:
        data = json.load(file)
    df = pd.DataFrame(data)
    # Split bbox coordinates into separate columns
    df[['x1', 'y1', 'x2', 'y2']] = pd.DataFrame(df['bbox'].tolist(), index=df.index)
    df = df.drop(columns=['bbox'])
    return df

def filter_content(df, size_check=False):
    # Remove boxes containing only digits
    new_df = df[~df['text'].str.isdigit()]
    if size_check:
        new_df = new_df[new_df['size'] >= 16]
    return new_df

def merge_semantic_rows(df):
    if len(df) == 8:  # Skip processing for normal dataframes
        return df
    
    merged_data = []
    buffer = None

    for _, row in df.iterrows():
        text = row['text']
        if buffer is None:
            buffer = row.copy()
        else:
            # Check if current line should be merged with previous
            if not buffer['text'].strip()[-1] in '.!?,:' and not text.strip()[0].isupper() and not text.strip()[0].isdigit():
                buffer['text'] += " " + text.strip()
            else:
                merged_data.append(buffer)
                buffer = row.copy()

    if buffer is not None:
        merged_data.append(buffer)

    return pd.DataFrame(merged_data)

def group_by_x_coordinate(df, tolerance=20):
    df = df.sort_values(by='x', ascending=False)
    groups = []
    current_group = []
    last_x = None

    for _, row in df.iterrows():
        x, y = row['x'], row['y']
        if last_x is None or abs(x - last_x) <= tolerance:
            current_group.append(row)
        else:
            group_df = pd.DataFrame(current_group).sort_values(by='y', ascending=True)
            groups.append(group_df)
            current_group = [row]
        last_x = x

    if current_group:
        group_df = pd.DataFrame(current_group).sort_values(by='y', ascending=True)
        groups.append(group_df)
    return groups

def group_by_y_coordinate(df, y_tolerance=10):
    new_rows = []
    current_row = None

    for _, row in df.iterrows():
        if current_row is None:
            current_row = row
        else:
            if abs(current_row['y2'] - row['y2']) < y_tolerance:
                current_row['text'] += " " + row['text']
            else:
                new_rows.append(current_row)
                current_row = row

    if current_row is not None:
        new_rows.append(current_row)

    return pd.DataFrame(new_rows)

def is_vietnamese_text(text):
    vietnamese_pattern = re.compile(r'[a-zA-ZÀ-ỹ]+', re.UNICODE)
    return bool(vietnamese_pattern.search(text))

def split_vietnamese_content(df):
    df['Contains_Vietnamese'] = df['text'].apply(is_vietnamese_text)
    
    df_vietnamese = df[df['Contains_Vietnamese']].copy()
    df_non_vietnamese = df[~df['Contains_Vietnamese']].copy()
    
    # Calculate center coordinates
    for split_df in [df_vietnamese, df_non_vietnamese]:
        split_df['x'] = (split_df['x1'] + split_df['x2']) / 2
        split_df['y'] = (split_df['y1'] + split_df['y2']) / 2
    
    return df_vietnamese, df_non_vietnamese

def fix_translation_alignment(df, translations):
    i = 0
    translate_results = []
    
    while i < len(translations):
        current_text = df.loc[len(translate_results), "SinoVietnamese Text"]
        
        if current_text == "Tử Viết" and not translations[i].strip().endswith(":"):
            parts = translations[i].split(":", 1)
            if len(parts) == 2:
                translate_results.append(parts[0] + ":")
                translate_results.append(parts[1].strip())
            else:
                translate_results.append(translations[i])
            i += 1
        else:
            translate_results.append(translations[i])
            i += 1

    while len(translate_results) < len(df):
        translate_results.append(None)

    df["Vietnamese Translation"] = translate_results
    return df

def process_page_pair(page_number, skip_translation=False):
    # Process main content page
    filename1 = f'output/text/HaiChau_Luan Ngu C4_page{page_number:03}.json'
    df1 = create_dataframe(filename1)
    df1 = filter_content(df1)
    df_vietnamese, df_non_vietnamese = split_vietnamese_content(df1)
    groups_vietnamese = group_by_x_coordinate(df_vietnamese)
    groups_non_vietnamese = group_by_x_coordinate(df_non_vietnamese)

    # Process translation page
    filename2 = f'output/text/HaiChau_Luan Ngu C4_page{page_number + 1:03}.json'
    df2 = create_dataframe(filename2)
    df2 = filter_content(df2, True)
    df2 = group_by_y_coordinate(df2)
    df2 = merge_semantic_rows(df2)

    # Prepare output filename and ID
    image_filename = filename1.replace('json', 'png')
    base_name = os.path.basename(image_filename)
    name, _ = os.path.splitext(base_name)
    
    if "_page" in name:
        prefix, page_number_str = name.split("_page")
        page_number = int(page_number_str)
    else:
        raise ValueError("Invalid filename format. Expected '_pageNNN' format.")
    
    # Copy image to label directory
    shutil.copy(f'output/images/HaiChau_Luan Ngu C4_page{page_number:03}.png', 'images_label')

    # Create output DataFrame
    result_df = pd.DataFrame(columns=["Image Name", "ID", "Box", "SinoNom Text", "SinoVietnamese Text", "Vietnamese Translation"])

    # Handle translations
    if skip_translation:
        translations = [""] * len(groups_non_vietnamese)
    else:
        if len(df2['text']) < len(groups_non_vietnamese):
            translations = [""] * len(groups_non_vietnamese)
            needs_alignment_fix = True
        else:
            translations = df2['text'].tolist()
            needs_alignment_fix = False

    # Combine content
    for idx, (group_non_viet, group_viet, translation) in enumerate(zip(groups_non_vietnamese, groups_vietnamese, translations)):
        x1 = int(group_non_viet['x1'].min())
        x2 = int(group_non_viet['x2'].min())
        y1 = int(group_non_viet['y1'].min())
        y2 = int(group_non_viet['y2'].max())

        box = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
        ID = f"{prefix}.{page_number:03}.{idx + 1:03}"

        non_viet_text = " ".join(group_non_viet["text"])
        viet_text = " ".join(group_viet["text"])
        
        result_df.loc[len(result_df)] = [base_name, ID, box, non_viet_text, viet_text, translation]
    
    if needs_alignment_fix:
        result_df = fix_translation_alignment(result_df, df2['text'].tolist())
        
    return result_df

def process_document(start_page=5, end_page=191, skip_pages=[]):
    df = pd.DataFrame(columns=["Image Name", "ID", "Box", "SinoNom Text", "SinoVietnamese Text", "Vietnamese Translation"])
    
    for page_num in range(start_page, end_page, 2):
        try:
            skip_translation = (page_num + 1) in skip_pages
            new_df = process_page_pair(page_num, skip_translation)
            
            if not new_df.empty:
                df = pd.concat([df, new_df])
                print(f"Successfully processed pages {page_num} and {page_num + 1}")
        except Exception as e:
            print(f"Error processing pages {page_num} and {page_num + 1}: {str(e)}")
            continue
            
    return df

def save_to_excel(df, output_file):
    df.to_excel(output_file, index=False, engine='openpyxl')
    
    # Format Excel columns
    workbook = load_workbook(output_file)
    sheet = workbook.active
    
    for column in sheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                max_length = max(max_length, len(str(cell.value)))
            except:
                pass
        
        sheet.column_dimensions[column_letter].width = max_length + 2
    
    workbook.save(output_file)
    print(f"Excel file saved to: {output_file}")

def main():
    # Extract content from PDF
    pdf_filename = "HaiChau_Luan Ngu C4.pdf"
    extract_pdf_content(pdf_filename, 'output/')
    
    # Process document content
    df = process_document()
    
    # Save results
    save_to_excel(df, 'output.xlsx')

if __name__ == "__main__":
    main()