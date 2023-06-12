import random
import time
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


def start_driver():
    chrome_driver_path = './chromedriver_mac64/chromedriver'
    service = Service(executable_path=chrome_driver_path)

    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    return driver


def collect_links(driver, url, by, article_element):
    driver.get(url)
    elements = driver.find_elements(by,
                                    article_element)
    links = [el.get_attribute('href') for el in elements]
    return links


class ScrapperWithPageNum:
    def __init__(self, main_body):
        self.main_body = main_body

    def select_page(self, param_body, iterating_number):
        news_link = f'{self.main_body}{param_body}{iterating_number}/'

        return news_link

    @staticmethod
    def collect_links(soup, element, html_class):
        article_element = soup.find(element, html_class)
        a_tags = article_element.find_all('a')
        urls = [tag.get('href') for tag in a_tags]

        return urls

    @staticmethod
    def collect_date(by, date_element):
        return driver.find_element(by, date_element)

    @staticmethod
    def collect_category(by, category_element):
        return driver.find_element(by, category_element)

    @staticmethod
    def collect_text(by, text_element):
        return driver.find_element(by, text_element)

    @staticmethod
    def collect_content(self, url, article_element):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html.parser')
        content = soup.find('article', re.compile(f'^{article_element}'))

        return content


scrapper = ScrapperWithPageNum('https://news.microsoft.com/category/press-releases')

scrapped_list = []
driver = start_driver()
for i in range(1, 535):  # 1034 is the MAX value
    webpage = scrapper.select_page('/page/', i)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for link in links:
        print(link)
        driver.get(link)
        try:
            datetime_element = driver.find_element(By.XPATH, "//time")
            try:
                date_timestamp = datetime_element.get_attribute("datetime")
                dt_object = datetime.fromtimestamp(int(date_timestamp))
                date = dt_object.strftime('%Y-%m-%d')
            except ValueError:
                dt_object = re.findall('(?<=)(.*?)(?=T)', str(date_timestamp))
                date = dt_object[0]

            text_element = scrapper.collect_text(By.XPATH, '//section')
            text = text_element.text
        except NoSuchElementException:
            date = None
            text = None
        scrapped_list.append({'url': link,
                              'date': date,
                              'category': None,
                              'text': text
                              })
        time.sleep(random.randint(0, 3))

scrapped_df = pd.DataFrame(scrapped_list)
scrapped_df.to_csv('microsoft_news_text_1.csv')
