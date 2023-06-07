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
        print(news_link)

        return news_link

    def collect_links(self, soup, element, html_class):
        article_element = soup.find(element, html_class)
        a_tags = article_element.find_all('a')
        links = [tag.get('href') for tag in a_tags]

        return links

    def collect_date(self, content, element, date_element):
        return content.find(element, date_element).get_text()

    def collect_category(self, content, element, category_element):  # category-eyebrow__
        return content.find(element, class_=re.compile(f'^{category_element}')).get_text()

    def collect_text(self, content, element, text_element1,
                     text_element2):  # div, 'hero-headline', 'pagebody text component'
        return content.find(element, [text_element1, text_element2]).get_text()

    def collect_content(self, link, article_element):
        r = requests.get('https://blogs.microsoft.com/blog/2023/02/22/the-new-bing-preview-experience-arrives-on-bing-and-edge-mobile-apps-introducing-bing-now-in-skype/')
        soup = BeautifulSoup(r.content, 'html.parser')
        content = soup.find(re.compile(f'^{article_element}'))

        return content


scapper = ScrapperWithPageNum('https://blogs.microsoft.com')
info_list = []
driver = start_driver()
for i in range(2, 5):
    webpage = scapper.select_page('/page/', i)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')
    for link in links:
        content = scapper.collect_content(link, 'post entry m-blog-post post-')
        print(content)
        date = scapper.collect_date(content, 'p', 'c-meta-text')
        # category = scapper.collect_category(content, 'span', 'category-eyebrow__')
        # text = scapper.collect_text(content, 'div', 'hero-headline', 'pagebody text component')

        info_list.append({'url': link,
                          'date': date,
                          'category': category,
                          'text': text
                          })

test = pd.DataFrame(info_list)
# test.to_csv('apple_newsroom_text.csv')
