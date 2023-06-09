import random
import time
import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
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


def collect_links(driver, link, by, article_element):
    driver.get(link)
    elements = driver.find_elements(by,
                                    article_element)
    links = [el.get_attribute('href') for el in elements]
    return links


class ScrapperWithPageNum:
    def __init__(self, main_body):
        self.main_body = main_body

    def select_page(self, param_body, i):
        news_link = f'{self.main_body}{param_body}{i}/'

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


scrapper = ScrapperWithPageNum('https://blogs.microsoft.com')
info_list = []
driver = start_driver()
for i in range(2, 226):  # 226 is the MAX value
    webpage = scrapper.select_page('/page/', i)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for link in links:
        print(link)
        driver.get(link)

        datetime_element = driver.find_element(By.XPATH, "//time")
        date = datetime_element.get_attribute("datetime")

        text_element = scrapper.collect_text(By.XPATH, '//article')
        text = text_element.text

        info_list.append({'url': link,
                          'date': date,
                          'category': '---',
                          'text': text
                          })
        time.sleep(random.randint(0, 3))

test = pd.DataFrame(info_list)
# test.to_csv('apple_newsroom_text.csv')
