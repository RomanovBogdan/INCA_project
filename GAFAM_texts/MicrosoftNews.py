import random
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def start_driver():
    chrome_driver_path = './chromedriver-mac-arm64/chromedriver'
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


def convert_timestamp(date_timestamp):
    dt_object = datetime.fromtimestamp(int(date_timestamp), timezone.utc)
    return dt_object


def collect_text(soup):
    entry_content = soup.find("div", "entry-content")
    for i in entry_content.find_all('figure'):
        i.extract()

    for i in entry_content.find_all('p', 'tag-list'):
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
phrases_to_remove_after = [
    "For more information, press only:",
    "For further information",
    "Editor’s note ",
    'Note to editors: '
    "Media Contacts"
]

last_page = 1036
driver = start_driver()

for page_number in range(1, 1036):
    print(f"Processing page {page_number} of {last_page - 1}...")
    webpage = select_page(main_body, '/page/', page_number)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for link_number, link in enumerate(links):
        driver.get(link)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find("h1", "entry-title").get_text()
        date_timestamp = soup.find("time")['datetime']
        text_list = collect_text(soup)
        sorted_text = filter_text(text_list, phrases_to_remove_after)
        scraped_list.append({'url': link,
                             'title': title,
                             'date': convert_timestamp(date_timestamp),
                             'text': ''.join(text_list),
                             'sorted_text': ''.join(sorted_text)
                             })

        time.sleep(random.randint(0, 3))
        print(f"\tProcessed link {link_number} of {len(links)} on page {page_number}.")

text_df = pd.DataFrame(scraped_list)
