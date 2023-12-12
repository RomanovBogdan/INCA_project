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


def collect_text(soup, tag, element_class):
    entry_content = soup.find(tag, element_class)
    if not entry_content:
        return []

    # Assuming you want to remove certain elements from entry_content
    for unwanted_element in entry_content.find_all('entry-downloads'):
        unwanted_element.extract()

    for unwanted_element in entry_content.find_all('entry-taxonomy'):
        unwanted_element.extract()

    return [i.get_text() for i in entry_content.find_all(['p', 'h2'])]



# links_list = []
# for page_number in range(1, 214):
#     # 213 is the MAX page_number
#     r = requests.get(f'https://about.fb.com/news/page/{page_number}/')
#     soup = BeautifulSoup(r.content, 'html.parser')
#
#     collect_links(soup, links_list)

links_list = pd.read_csv('./new_INCA_data/links/FacebookNews_links.csv', index_col=0)

scraped_list = []
exceptions = ['what-is-the-metaverse/', 'oversight-board']
for link_number, link in enumerate(links_list['0'][473:]):
    print(link)

    if any(except_part in link for except_part in exceptions):
        title = '-'
        date = '-'
        text_list = []
        print('This')
        continue

    else:
        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')

        try:
            date = soup.find('time')['datetime']
            date = pd.to_datetime(date)
        except TypeError:
            date = 'No separate element'
        except AttributeError:
            date = '-'

        header_element = soup.find('header', 'entry-header')
        if header_element:
            title = header_element.get_text()
        else:
            section_title_element = soup.find('h1', 'section-title')
            title = section_title_element.get_text() if section_title_element else None

        try:
            takeaways = soup.find('div', 'the-highlights').get_text()
        except AttributeError:
            takeaways = ''
            print('No takeaways section')

        text_list = collect_text(soup, 'div', 'entry-content')
        if text_list:
            text_list.insert(0, takeaways)
        else:
            text_list = collect_text(soup, 'div', 'desc')

    scraped_list.append({'url': link,
                         'title': title,
                         'date': date,
                         'text': ' '.join(text_list)
                         })
    time.sleep(random.randint(1, 2))
    print(f"\tProcessed link {link_number+1} of {len(links_list)}")

scraped_df = pd.DataFrame(scraped_list)
scraped_df.to_csv('new_INCA_data/FacebookNews_data.csv')
