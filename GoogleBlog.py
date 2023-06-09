import pandas as pd
import requests
import re
from datetime import datetime
import json
from bs4 import BeautifulSoup


def log(message: str, page_url):
    logfile = f"google_log.txt"
    timestamp_format = '%Y-%h-%d-%H:%M:%S'
    now = datetime.now()
    timestamp = now.strftime(timestamp_format)
    with open(logfile, "a") as f:
        f.write(timestamp + ', ' + f'{message}' + ': ' + f'{page_url}' + '\n')

info_list = []
for cursor in range(1, 702):
    url = f"https://blog.google/api/v2/latest?cursor={cursor}"
    log('Collecting the data from the', url)
    response = requests.get(url)
    test = json.loads(response.text)
    for result in test['results']:
        date_element = result['published']
        date = re.findall('(?<='')(.*?)(?=T)', str(date_element))
        log('Collecting date object, here it is', date)

        category = result['category']
        link = result['full_url']

        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')
        main_elements = soup.find_all('div', attrs={'class': 'rich-text'})
        text = [i.get_text() for i in main_elements]
        text = ' '.join(text)

        info_list.append({'url': link,
                          'date': date[0],
                          'category': category,
                          'text': text
                          })

test = pd.DataFrame(info_list)
test.to_csv('google_blog_text.csv')