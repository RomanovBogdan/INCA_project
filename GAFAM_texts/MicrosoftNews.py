import random
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timezone
from bs4 import BeautifulSoup

def start_driver(chrome_driver_path):
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


def collect_links(driver, url, by, article_element):
    driver.get(url)
    elements = driver.find_elements(by, article_element)
    links = [el.get_attribute('href') for el in elements]
    return links


def select_page(main_body, param_body, iterating_number):
    news_link = f'{main_body}{param_body}{iterating_number}/'
    return news_link


def collect_title(by, title_element):
    return driver.find_element(by, title_element).text

def collect_date_from_timestamp(by, date_element):
    datetime_element = driver.find_element(by, date_element)
    date_timestamp = datetime_element.get_attribute("datetime")
    dt_object = datetime.fromtimestamp(int(date_timestamp), timezone.utc)
    return dt_object

def collect_text():
    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')
    entry_content = soup.find("div", "entry-content")
    for i in entry_content.find_all('figure'):
        i.extract()

    text_list = [i.get_text() for i in entry_content.find_all('p')]
    return text_list

def filter_text(text_list, phrases_to_remove_after):
    for i, text in enumerate(text_list):
        if any(phrase in text for phrase in phrases_to_remove_after):
            return text_list[:i]
    return text_list

main_body = 'https://news.microsoft.com/category/press-releases'
scraped_list = []
chrome_driver_path = './chromedriver-mac-arm64/chromedriver'
iteration = 1
phrases_to_remove_after = [
    "For more information, press only:",
    "For further information",
    "Editor's note",
    "Media Contacts"
]

last_page = 3
driver = start_driver(chrome_driver_path)

for page_number in range(1, last_page):
    webpage = select_page(main_body, '/page/', page_number)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for i, link in enumerate(links):
        driver.get(link)
        text_list = collect_text()
        sorted_text = filter_text(text_list, phrases_to_remove_after)
        scraped_list.append({'url': link,
                             'title': collect_title(By.CLASS_NAME, 'entry-title'),
                             'date': collect_date_from_timestamp(By.TAG_NAME, 'time'),
                             'text': text_list,
                             'len': len(text_list),
                             'sorted_text': sorted_text,
                             'len_sorted': len(sorted_text)
                             })

        time.sleep(random.randint(0, 3))
        print(f'Collected {iteration} out of {len(links) * (last_page - 1)}')
        iteration += 1

text_df = pd.DataFrame(scraped_list)
text_df.iloc[13, :].url