import random
import re
import time
import pandas as pd
import requests
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup


def start_driver():
    chrome_driver_path = './chromedriver-mac-arm64/chromedriver'
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


def collect_links(driver, existing_links):
    title_elements = driver.find_elements(By.CLASS_NAME, 'PromoCardSearchResults-title')
    len(title_elements)
    for title_element in title_elements:
        link_element = title_element.find_element(By.TAG_NAME, "a")
        link_url = link_element.get_attribute('href')
        if link_url not in existing_links:
            existing_links.append(link_url)


def press_next_page_button(driver):
    next_page = driver.find_element(By.CLASS_NAME, 'SearchResultsModuleResults-nextPage-button')
    next_page.click()


def collect_all_news_links():
    main_body = 'https://www.aboutamazon.com/news'
    driver = start_driver()
    driver.get(main_body)
    all_links = []
    button_element = driver.find_element(By.CLASS_NAME, 'SearchResultsModuleResults-nextPage-button')
    while button_element:
        collect_links(driver, all_links)

        try:
            press_next_page_button(driver)
        except NoSuchElementException:
            print('No more pages to navigate to')
            break

        time.sleep(random.randint(1, 4))
        print(len(all_links))
    return all_links


def collect_text(beautiful_soup):
    sub_headline = ''
    opening_par = ''

    html_element = beautiful_soup.find('html')
    page_type = html_element['class']
    if page_type[0] == 'ArticlePage':
        entry_content = beautiful_soup.find('article', class_=re.compile(r"-mainContent$"))
    else:
        entry_content = beautiful_soup.find('div', class_=re.compile(r"-mainContent$"))
    try:
        sub_headline = beautiful_soup.find('div', class_=re.compile(r'-subHeadline$')).get_text()
        opening_par = beautiful_soup.find('div', 'RichTextArticleBody').get_text()
    except AttributeError:
        print('No sub headline')
    text_data_list = [i.get_text() for i in entry_content.find_all(['p', 'h2', 'cms-headings-h2'])]
    if len(text_data_list) == 0:
        text_data_list = [i.get_text() for i in entry_content.find_all(['li', 'ListicleItem-title'])]
        text_data_list.insert(0, opening_par)
    text_data_list.insert(0, sub_headline)
    return text_data_list


def convert_to_datetime(date_string):
    date_str_without_z = date_string[:-1]
    date_object = datetime.fromisoformat(date_str_without_z)
    return date_object


links_list = pd.read_csv('./new_INCA_data/links/AmazonNews_links.csv', index_col=0)

scraped_list = []
for link_number, link in enumerate(links_list['0']):
    print(link)

    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    title = soup.find('h1').get_text()

    timestamp_element = soup.find('bsp-timestamp')
    date_obj = ''
    try:
        date_str = timestamp_element['data-timestamp']
        try:
            date_obj = convert_to_datetime(date_str)
        except ValueError:
            date_obj = datetime.utcfromtimestamp(int(date_str)/1000)
    except:
        date_str = timestamp_element['data-timestamp-iso']
        date_obj = convert_to_datetime(date_str)

    text_list = collect_text(soup)

    scraped_list.append({'url': link,
                         'title': title,
                         'date': date_obj,
                         'text': ' '.join(text_list)
                         })

    time.sleep(random.randint(1, 2))
    print(f"\tProcessed link {link_number+1} of {len(links_list)}")

scraped_df = pd.DataFrame(scraped_list)
scraped_df.to_csv('new_INCA_data/AmazonNews_data.csv')
