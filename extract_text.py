import fitz  # PyMuPDF
import json
import os
import pandas as pd
from io import StringIO
# import easyocr
import regex as re
# from transformers import pipeline
from openpyxl import load_workbook
from xlsxwriter import Workbook 


file = "Data/HaiChau_Luan Ngu C4.pdf"
text_dir = f'./extracted_text/'
dict_dir = f'./extracted_dict/'

# file_name = (file.split('/')[-1]).split('.')[0]
# OCR_res_path = f'./detected_images/{file_name}/Label.txt'
# images_dir = f'./detected_images/{file_name}/'
# metadata_dir = f'./metadata/{file_name}/'


def extract_text_from_pdf(pdf_path, text_dir):
    # Open the PDF file
    document = fitz.open(pdf_path)
    # text = ""
    
    # Create directories if they don't exist
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)
    # if not os.path.exists(dict_dir):
    #     os.makedirs(dict_dir)

    # Iterate through pages and extract text
    for page_number in range(len(document)):
        text_file= f"{text_dir}page_{page_number}.txt" 
        # dict_file= f"{dict_dir}page_{page_number}.json"
        
        print(f"Processing page {page_number}")
        print(f"Extracting text from page {page_number}")
        
        page = document[page_number]
        dictionary_elements = page.get_text('dict')
        with open(text_file, "w", encoding = "utf-8-sig") as text_file:
            for block in dictionary_elements['blocks']:
                if 'lines' not in block:
                    continue
                for line in block['lines']:
                    for span in line['spans']:
                        line_text = span['text'].strip()
                        if line_text == '':
                            continue
                        text_file.write(f"text: {line_text}\n")
                        text_file.write(f"bbox: {span['bbox']}\n")        
    # Close the document
    document.close()



# Extract and print the text
extracted_text = extract_text_from_pdf(file, text_dir)
# print(extracted_text)
