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

facebook_news = {'link': 'https://about.fb.com/news/',
                'by_1': By.CLASS_NAME,
                'button_element': 'show-more-wrapper',
                'by_2': By.CSS_SELECTOR,
                'article_element': 'article-preview article-card loop-card show has-image post-'
                }



class GAFAM_scrapper:
    def __init__(self, link, by_1, button_element, by_2, article_element):
        self.link = link
        self.by_1 = by_1
        self.button_element = button_element
        self.by_2 = by_2
        self.article_element = article_element

    def start_driver(self):
        chrome_driver_path = './chromedriver_mac64/chromedriver'
        service = Service(executable_path=chrome_driver_path)

        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get(self.link)
        return driver

    def collect_links(self, driver):
        elements = driver.find_elements(self.by_2,
                                        self.article_element)
        links = [el.get_attribute('href') for el in elements]
        return links

    def find_click_next_page(self, driver):
        all_links = []  # initialize the list to store all links
        num_links = 0  # keep track of the number of links collected so far

        while True:
            try:
                # collect links on the current page
                elements = driver.find_elements(self.by_2, self.article_element)
                new_links = [el.get_attribute('href') for el in elements[num_links:]]  # only collect new links
                all_links.extend(new_links)  # add the new links to our list

                num_links = len(elements)  # update the number of links collected so far

                next_page = driver.find_element(self.by_1, self.button_element)
                next_page.click()
                time.sleep(random.randint(0, 4))
            except NoSuchElementException:
                print(1)
                break
            except StaleElementReferenceException:
                print(2)
                continue
            except ElementClickInterceptedException:
                print(3)
                continue

        return all_links  # return the collected links when there are no more pages


try:
    all_links = []
    scrapper = GAFAM_scrapper(facebook_news['link'],
                              facebook_news['by_1'],
                              facebook_news['button_element'],
                              facebook_news['by_2'],
                              facebook_news['article_element'])
    driver = scrapper.start_driver()
    all_links = scrapper.find_click_next_page(driver)
except:
    print('Oops')