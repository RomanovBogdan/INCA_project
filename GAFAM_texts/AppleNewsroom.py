import time
import random
import requests
import pandas as pd
from bs4 import BeautifulSoup


def select_page(url_main_body, param_body, page_num):
    news_link = f'{url_main_body}{param_body}{page_num}'
    r = requests.get(news_link)
    beautiful_soup = BeautifulSoup(r.content, 'html.parser')
    return beautiful_soup


def collect_links(beautiful_soup, element, html_class):
    article_element = beautiful_soup.find(element, html_class)
    a_tags = article_element.find_all('a')
    links = [tag.get('href') for tag in a_tags]
    return links


def collect_element(beautiful_soup, element, element_name):
    return beautiful_soup.find(element, element_name).get_text()


def generate_full_link(url_main_body, article_link):
    full_page_link = f'{url_main_body}{article_link}'
    # print(full_page_link)
    return full_page_link


def collect_text(beautiful_soup):
    entry_content = soup.find('article')

    for i in entry_content.find_all('div', 'presscontacts'):
        i.extract()

    for i in entry_content.find_all('aside', 'component'):
        i.extract()

    text_data_list = [i.get_text() for i in entry_content.find_all('div', ['featured-subhead', 'pagebody-copy'])]
    return text_data_list


def filter_text(text_data_list, phrases_to_remove_after):
    for i, text in enumerate(text_list):
        print(i, text)
        if any(phrase in text for phrase in phrases_to_remove_after):
            return text_data_list[:i]
    return text_data_list


main_body = 'https://www.apple.com/'
scraped_list = []
last_page = 211
remove_phrases = [
    'Press Contacts'
]


for page_number in range(1, last_page):
    # 211 is MAX value for page_num

    print(f"Processing page {page_number} of {last_page - 1}...")

    soup = select_page(main_body, '/newsroom/archive/?page=', page_number)
    links_list = collect_links(soup, 'div', 'results')
    for link_number, link in enumerate(links_list):
        print(link_number, link)
        page_link = generate_full_link(main_body, link)

        r = requests.get(link)
        soup = BeautifulSoup(r.content, 'html.parser')

        page_type = soup.find('title').get_text()

        if 'Page Not Found' in page_type:
            continue
        else:
            title = collect_element(soup, 'h1', ['hero-headline', 'headersplitview__title'])

            date = collect_element(soup, 'span', 'category-eyebrow__date')

            text_list = collect_text(soup)

        scraped_list.append({'url': link,
                             'title': title,
                             'date': date,
                             'text': ' '.join(text_list),
                             'sorted_text': ' '.join(filter_text(text_list, remove_phrases))
                             })

        time.sleep(random.randint(1, 2))
        print(f"\tProcessed link {link_number + 1} of {len(links_list)}")

scraped_df = pd.DataFrame(scraped_list)
scraped_df.to_csv('new_INCA_data/AppleNewsroom_data.csv')
