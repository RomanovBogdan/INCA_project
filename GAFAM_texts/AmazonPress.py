import random
import re
import time
import pandas as pd
import requests
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.chrome.service import Service
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


def collect_all_links():
    main_body = 'https://press.aboutamazon.com/press-release-archive'
    driver = start_driver()
    driver.get(main_body)
    all_links = []
    i = 0
    # CHANGE WHILE CONDITION
    while i != 20:
        collect_links(driver, all_links)
        print(i, len(all_links))
        press_next_page_button(driver)
        time.sleep(random.randint(1, 4))
        i += 1
    return all_links


def collect_text(soup):
    entry_content = soup.find('article', class_=re.compile(r"-mainContent$"))
    text_list = [i.get_text() for i in entry_content.find_all('p')]
    return text_list


def convert_to_datetime(date_string):
    date_str = date_string[:-1]
    date_obj = datetime.fromisoformat(date_str)
    return date_obj


def filter_text(text_list, phrases_to_remove_after):
    for i, text in enumerate(text_list):
        if any(phrase in text for phrase in phrases_to_remove_after):
            return text_list[:i]
    return text_list


links = collect_all_links()


scraped_list = []
phrases_to_remove_after = [
    "About Amazon",
    'About Amazon Web Services',
    'About\xa0Amazon'
]

for link in links:
    print(link)

    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")
    try:
        title = soup.find('h1').get_text()

        timestamp_element = soup.find('bsp-timestamp')
        date_str = timestamp_element['data-timestamp-iso']
        date_obj = convert_to_datetime(date_str)

        text_list = collect_text(soup)

    except AttributeError:
        title = soup.find('module-details_title')

    sorted_text_list = filter_text(text_list, phrases_to_remove_after)

    scraped_list.append({'url': link,
                         'title': title,
                         'date': date_obj,
                         'text': ' '.join(text_list),
                         'sorted_text': ' '.join(sorted_text_list)
                         })

scraped_df = pd.DataFrame(scraped_list)
