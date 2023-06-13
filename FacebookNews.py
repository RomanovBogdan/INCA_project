import random
import re
import time
import pandas as pd
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

link_list = []
for page_number in range(1, 211):  # 210 is the MAX page_number

    r = requests.get(f'https://about.fb.com/news/page/{page_number}/')

    soup = BeautifulSoup(r.content, 'html.parser')

    posts_div = soup.find('div', class_='posts')
    links = posts_div.find_all('a', href=True)
    for link in links:
        link_list.append(link['href'])

links_df = pd.DataFrame(link_list)
links_df = links_df.drop_duplicates().reset_index(drop=True)
links_df.to_csv('facebook_news_links.csv')

scrapped_list = []
for num, link in enumerate(links_df[0]):
    print(num)
    r = requests.get(link)
    soup = BeautifulSoup(r.content, 'html.parser')

    try:
        date = soup.find('time')['datetime']
        date = re.findall('(?<=)(.*?)(?=T)', str(date))
        date = date[0]

        #date_string = '2023-05-17T10:00:10-07:00'
        #date_only = date_string.split('T')[0]

        text = soup.find('div', 'uk-width-2-3@m article-container').get_text()
        text_cl = re.sub('\t', '', text)
        text_cl = re.sub('\n', ' ', text_cl)
        text = re.sub(' +', ' ', text_cl)

    except TypeError:
        date = None
        text = None

    scrapped_list.append({'url': link,
                          'date': date,
                          'category': None,
                          'text': text
                          })
    time.sleep(random.randint(0,3))

scrapped_df = pd.DataFrame(scrapped_list)
print(scrapped_df)
scrapped_df.to_csv('facebook_news_text.csv')