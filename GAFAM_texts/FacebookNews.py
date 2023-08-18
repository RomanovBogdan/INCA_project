import random
import time
import pandas as pd
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def collect_links(beautiful_soup, existing_links):
    posts_div = beautiful_soup.find('div', class_='posts')
    links = posts_div.find_all('a', href=True)
    for one_link in links:
        if one_link['href'] not in existing_links:
            existing_links.append(one_link['href'])


def convert_timestamp(date_timestamp):
    dt_object = datetime.fromtimestamp(int(date_timestamp), timezone.utc)
    return dt_object


links_list = []
for page_number in range(1, 5):
    # CHANGE THE RANGE VALUES
    # 213 is the MAX page_number
    r = requests.get(f'https://about.fb.com/news/page/1/')
    soup = BeautifulSoup(r.content, 'html.parser')

    collect_links(soup, links_list)


scraped_list = []
for link_number, link in enumerate(links_list):
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    date = soup.find('time')['datetime']
    date = pd.to_datetime(date)

    title = soup.find('header', 'entry-header').get_text()

    text = soup.find('div', 'entry-content').get_text()

    scraped_list.append({'url': link,
                         'title': title,
                         'date': date.to_pydatetime(),
                         'text': text
                         })
    time.sleep(random.randint(2, 4))
    print(f"\tProcessed link {link_number+1} of {len(links_list)}")

scraped_df = pd.DataFrame(scraped_list)
