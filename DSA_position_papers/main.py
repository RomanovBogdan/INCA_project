import PyPDF2
import os
import re
import pandas as pd
import pytesseract
from pdf2image import convert_from_path


def extract_text_from_pdf(file_path):
    pdf_file_obj = open(file_path, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page_obj = pdf_reader.pages[page_num]
        text += page_obj.extract_text()
        output_string = ' '.join(text.split())
    pdf_file_obj.close()
    return output_string


def get_files_from_folder(folder_name):
    links_list = []
    folders = os.listdir(os.getcwd() + '/' + folder_name)
    for folder in folders:
        link = os.getcwd() + '/Task_2_DSA_position_papers/' + folder
        for folder_path, folders, files in os.walk(link):
            for file in files:
                if '.pdf' in file:
                    links_list.append(link + '/' + file)
    return links_list


def clean_text(text):
    text = text.strip()
    text = re.sub('\n', '', text)
    return text


def extract_text_from_image(pdf_path):
    text = ''
    pages = convert_from_path(pdf_path)
    for i, page in enumerate(pages):
        text_tmp = str(pytesseract.image_to_string(page))
        text += text_tmp
        output_string = ' '.join(text.split())
    return output_string


def remove_links(text):
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+' \
                  r'|www\.(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.sub(url_pattern, '', text)


def remove_separators(text):
    consecutive_chars_pattern = r'(.)\1{2,}'
    return re.sub(consecutive_chars_pattern, ' ', text)


def max_length(text):
    length = [len(element) for element in text.split()]
    length.sort(reverse=True)
    return length[:5]


def collect_text_from_pdf(paths):
    data_list = []
    for i, pdf_path in enumerate(paths):
        print(i)
        try:
            text_pdf = extract_text_from_pdf(pdf_path)
            method = 'from PDF'
            if len(text_pdf) < 1500:
                text_pdf = extract_text_from_image(pdf_path)
                method = 'OCR due to short length'
        finally:
            cleaned_text = clean_text(text_pdf)
            data_list.append({'link': pdf_path,
                              'folder': pdf_path.split('/')[-2],
                              'file_name': pdf_path.split('/')[-1],
                              'text': cleaned_text,
                              'method': method,
                              'old_max_length': max_length(cleaned_text),
                              'new_max_length': max_length(remove_links(cleaned_text))})
    return data_list


pdf_paths = get_files_from_folder('Task_2_DSA_position_papers')
text_list = collect_text_from_pdf(pdf_paths)
text_df = pd.DataFrame(text_list)
text_df['len'] = text_df.text.apply(len)

def fix_corrupted_parsing(df, index):
    df.loc[index, 'text'] = extract_text_from_image(df.loc[index, 'link'])

fix_corrupted_parsing(text_df, 315)
fix_corrupted_parsing(text_df, 320)
fix_corrupted_parsing(text_df, 376)
fix_corrupted_parsing(text_df, 148)
fix_corrupted_parsing(text_df, 506)


text_df.drop(columns=['old_max_length', 'new_max_length']).to_csv('DSA_position_paper_improved.csv')
