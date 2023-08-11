import random
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from bs4 import BeautifulSoup


def start_driver():
    chrome_driver_path = './chromedriver-mac-arm64/chromedriver'
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


def select_page(main_body, param_body, iterating_number):
    news_link = f'{main_body}{param_body}{iterating_number}/'
    return news_link


def collect_links(driver, link, by, article_element):
    driver.get(link)
    elements = driver.find_elements(by, article_element)
    links = [el.get_attribute('href') for el in elements]
    return links


def collect_text(soup):
    entry_content = soup.find("div", "entry-content")
    for i in entry_content.find_all('figure'):
        i.extract()

    for i in entry_content.find_all('p', 'tag-list'):
        i.extract()

    text_list = [i.get_text() for i in entry_content.find_all('p')]
    return text_list


scraped_list = []
main_body = 'https://blogs.microsoft.com/'
last_page = 4

driver = start_driver()
for page_number in range(1, last_page):  # 226 is the MAX value
    print(f"Processing page {page_number} of {last_page - 1}...")
    webpage = select_page(main_body, '/page/', page_number)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for link_number, link in enumerate(links, start=1):
        driver.get(link)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find("h1", "entry-title").get_text()
        date_str = soup.find("time")['datetime']
        text_list = collect_text(soup)

        scraped_list.append({'url': link,
                             'title': title,
                             'date': datetime.strptime(date_str, '%Y-%m-%d'),
                             'text': ' '.join(text_list)
                             })
        print(f"\tProcessed link {link_number} of {len(links)} on page {page_number}.")

        time.sleep(random.randint(0, 3))

text_df = pd.DataFrame(scraped_list)
