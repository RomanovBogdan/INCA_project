import pandas as pd
import requests
import re
import json
from bs4 import BeautifulSoup
from datetime import datetime

scraped_list = []
last_cursor = 3

for cursor in range(1, last_cursor): # max(last_cursor) == 710
    print(f"Processing page {cursor} of {last_cursor - 1}...")
    url = f"https://blog.google/api/v2/latest?cursor={cursor}"
    response = requests.get(url)
    json_response = json.loads(response.text)
    for article_number, result in enumerate(json_response['results']):
        date_element = result['published']
        date = re.findall('(?<='')(.*?)(?=T)', str(date_element))

        r = requests.get(result['full_url'])
        soup = BeautifulSoup(r.content, 'html.parser')
        main_elements = soup.find_all('div', attrs={'class': 'rich-text'})
        text = ' '.join([i.get_text() for i in main_elements])

        scraped_list.append({'url': result['full_url'],
                             'title': result['headline'],
                             'date': datetime.strptime(date[0], '%Y-%m-%d'),
                             'text': text
                             })
        print(f"\tProcessed link {article_number+1} of {len(json_response['results'])} on page {cursor}.")

text_df = pd.DataFrame(scraped_list)

for page_num in range(200, 230):
    response = requests.get(f'https://blogs.microsoft.com/page/{page_num}/')
    if response.status_code != 200:
        print(f'The max page is {page_num}')
        break
    else:
        print('Not yet')
