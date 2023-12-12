import os
import re
import pandas as pd
import PyPDF2
from datetime import datetime


def get_pdf_files_from_folder(folder_name):
    """
    Retrieve a list of paths to PDF files within a given folder.

    Args:
    folder_name (str): The name of the folder to search in.

    Returns:
    list: A list of file paths for each PDF file found in the folder.
    """
    links_list = []
    base_path = os.path.join(os.getcwd(), folder_name)
    for folder_path, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith('.pdf'):
                links_list.append(os.path.join(folder_path, file))
    return links_list


files = get_pdf_files_from_folder('netherlands')


def extract_text_from_pdf(file_path):
    """
    Extract and concatenate text from all pages of a PDF file.

    Args:
    file_path (str): The file path of the PDF from which to extract text.

    Returns:
    str: The concatenated text extracted from the PDF.
    """
    with open(file_path, 'rb') as pdf_file_obj:
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page_obj = pdf_reader.pages[page_num]
            text += page_obj.extract_text() + "\n"
    return text


text_two = ''
for number, file in enumerate(files):
    print(f'This is PDF file {number+1} out of {len(files)}')
    text_list_two = extract_text_from_pdf(file)
    text_two = text_two + text_list_two

text_split = text_two.split('End of Document')


def extract_body(text):
    """
    Extract the body of text from a larger string based on a specific pattern.

    Args:
    text (str): The text to extract the body from.

    Returns:
    str: The extracted body of text.
    """
    pattern = r"Body(.*?)Load-Date"
    match = re.search(pattern, text, re.DOTALL)

    extracted_text = match.group(1).strip() if match else "Text not found"
    return extracted_text


def extract_loaddate(text):
    """
    Extract the load date from a text string.

    Args:
    text (str): The text from which to extract the load date.

    Returns:
    str: The extracted load date.
    """
    pattern = r"Load-Date:\s*(.*)"
    match = re.search(pattern, text)

    load_date = match.group(1).strip() if match else "Load-Date not found"
    return load_date


def extract_title_outlet_date(text):
    """
    Extract the title, outlet, and date from a given text.

    Args:
    text (str): The text from which to extract information.

    Returns:
    tuple: A tuple containing the title, outlet, and date.
    """
    text_lines = [line for line in text.split('\n') if line.strip()]

    date_patterns = [
        r'\d{1,2} \w+ \d{4} \w+',
        r'\w+ \d{1,2}, \d{4}',
        r'\d{1,2} \w+ \d{4} \w+ \d{1,2}:\d{2} [APM]{2} .+'
    ]

    def is_date_format(line):
        return any(re.match(pattern, line) for pattern in date_patterns)

    date_line_index = next((i for i, line in enumerate(text_lines) if is_date_format(line)), None)

    if date_line_index is not None:
        title = ' '.join(text_lines[:date_line_index - 1]).strip()
        outlet = text_lines[date_line_index - 1] if date_line_index - 1 < len(text_lines) else "Outlet not found"
        date = text_lines[date_line_index] if date_line_index < len(text_lines) else "Date not found"
    else:
        title = ' '.join(text_lines[:2]).strip()
        outlet = "Outlet not found"
        date = "Date not found"

    return title, outlet, date


def extract_head_first_page(text):
    """
    Extract the first section of text before a defined pattern.

    Args:
    text (str): The text from which to extract the section.

    Returns:
    str: The extracted section of text.
    """
    pattern = r"Timeline: \d{2} \w+ \d{4} \nto \d{2} \w+ \d{4}\n "
    text = re.split(pattern, text)
    final_element = text[-1]
    return final_element


final_list = []
errors = 0
for file in files:
    text_two = extract_text_from_pdf(file)
    text_split = text_two.split('End of Document')

    for text in text_split:
        try:
            title, outlet, date = extract_title_outlet_date(text)
            if date == 'Documents (100)':
                first_final_element = extract_head_first_page(text)
                title, outlet, date = extract_title_outlet_date(first_final_element)
            body = extract_body(text)
            load_date = extract_loaddate(text)
            final_list.append({
                'title': title,
                'outlet': outlet,
                'date': date,
                'main_text': body,
                'load_date': load_date,
                'file_path': file.split('/')[-1],
                'company_name': file.split('/')[-1].split()[0]
            })
        except Exception as e:
            print(f'Error processing document in file {file}: {e}')
            errors += 1


def remove_comma(date_str):
    """
    Remove commas from a date string.

    Args:
    date_str (str): The date string from which to remove commas.

    Returns:
    str: The date string with commas removed.
    """
    return date_str.replace(',', ' ')


def convert_bdy(date_str):
    """
    Convert a date string to a datetime object, expecting a specific format.

    Args:
    date_str (str): The date string to convert.

    Returns:
    datetime: The converted datetime object, or a string indicating the date was not found.
    """
    try:
        date_str = remove_comma(date_str)
        formatted_date_dt = datetime.strptime(date_str, '%B %d %Y')
    except ValueError:
        formatted_date_dt = 'Date not found'
    return formatted_date_dt


def convert_str_date_to_dt(date_str):
    """
    Convert a date string with various possible formats to a datetime object.

    Args:
    date_str (str): The date string to convert.

    Returns:
    datetime: The converted datetime object, or a string indicating the date was not found.
    """
    try:
        date_str = remove_comma(date_str)
    except ValueError:
        pass

    months = {'januari': 'January', 'februari': 'February', 'maart': 'March',
              'april': 'April', 'mei': 'May', 'juni': 'June',
              'juli': 'July', 'augustus': 'August', 'september': 'September',
              'oktober': 'October', 'november': 'November', 'december': 'December'}

    try:
        day, month, year = date_str.split()[:3]
        month_english = months[month.lower()]

        date_str_english = f"{day} {month_english} {year}"

        formatted_date_dt = datetime.strptime(date_str_english, '%d %B %Y')

    except KeyError:
        date_str = date_str.split()[:3]
        date_str = ' '.join(date_str)
        try:
            formatted_date_dt = convert_bdy(date_str)
        except ValueError:
            try:
                formatted_date_dt = datetime.strptime(date_str, '%d %B %Y')
            except ValueError:
                formatted_date_dt = 'Date not found'

    return formatted_date_dt


def fix_titles(title_str):
    """
    Fix and clean the titles extracted from the text.

    Args:
    title_str (str): The title string to be cleaned and fixed.

    Returns:
    str: The cleaned and fixed title.
    """
    title_str = title_str.replace('  ', ' ')
    if 'Timeline:' in title_str:
        title_split = title_str.split('Timeline:')
    else:
        title_split = title_str.split('Volkskrant')
    timeline_pattern = r"\d{2} [A-Za-z]{3} \d{4} to \d{2} [A-Za-z]{3} \d{4} "
    cleaned_text = re.sub(timeline_pattern, '', title_split[-1])
    return cleaned_text.strip()


def remove_section(text):
    """
    Remove specific sections from the text, such as 'Graphic' and 'Classification'.

    Args:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text.
    """
    cleaned_text = re.sub(r'Graphic.*', '', text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Classification.*', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Bekijk de oorspronkelijke pagina:.*', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'PDF-bestand van dit document', '', cleaned_text, flags=re.DOTALL)
    return cleaned_text


def remove_text_without_new_line(text):
    """
    Remove a specific pattern of text without a new line from the given text.

    Args:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text.
    """
    pattern = r'\nPage \d+ of \d+\n.*'
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return cleaned_text


def remove_text_with_new_line(text):
    """
    Remove a specific pattern of text with a new line from the given text.

    Args:
    text (str): The text to be cleaned.

    Returns:
    str: The cleaned text.
    """
    pattern = r'\nPage \d+ of \d+\n.*?\n'
    cleaned_text = re.sub(pattern, '', text, flags=re.DOTALL)
    return cleaned_text


final_df = pd.DataFrame(final_list)
subset = final_df[final_df.date == 'Date not found']

final_df.date = final_df.date.apply(convert_str_date_to_dt)
final_df.load_date = final_df.load_date.apply(convert_bdy)

final_df['title'] = final_df['title'].apply(fix_titles)
final_df['main_text'] = final_df['main_text'].apply(remove_section)
final_df['main_text'] = final_df['main_text'].apply(remove_text_with_new_line)
final_df['main_text'] = final_df['main_text'].apply(remove_text_without_new_line)
