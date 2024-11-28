import fitz  # PyMuPDF
import json
import os
import regex as re


def extract_text_from_pdf(pdf_path, output_dir):
    # Open the PDF file
    document = fitz.open(pdf_path)
       
    # Create directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for page_number in range(len(document)):
        page_text_file= f"{output_dir}page_{page_number}.json" 
        
        print(f"Processing page {page_number}")
        print(f"Extracting text and bbox from page {page_number}")
        
        page = document[page_number]
        dictionary_elements = page.get_text('dict')
        text_data = []
        for block in dictionary_elements['blocks']:
            if 'lines' not in block:
                continue
            for line in block['lines']:
                for span in line['spans']:
                    line_text = span['text'].strip()
                    if line_text == '':
                        continue
                    text_data.append({
                        'text': line_text,
                        'bbox': span['bbox']
                    })
        
        with open(page_text_file, 'w', encoding='utf-8-sig') as f:
            json.dump(text_data, f, ensure_ascii=False, indent=4)
    # Close the document
    document.close()

