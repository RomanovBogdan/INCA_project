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

amazon_press = {'link': 'https://press.aboutamazon.com/press-release-archive',
                'by_1': By.CLASS_NAME,
                'button_element': 'SearchResultsModuleResults-nextPage-button',
                'by_2': By.XPATH,
                'article_element': '//div[@class="PromoCardSearchResults-title"]//a'
                }

amazon_news = {'link': 'https://www.aboutamazon.com/news',
               'by_1': By.CLASS_NAME,
               'button_element': 'SearchResultsModuleResults-nextPage-button',
               'by_2': By.XPATH,
               'article_element': '//div[@class="PromoCardSearchResults-title"]//a'
               }

sources = {'amazon_press': amazon_press, 'amazon_news': amazon_news}


class GAFAMScrapper:
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
        all_links = []
        num_links = 0

        while True:
            try:
                elements = driver.find_elements(self.by_2, self.article_element)
                new_links = [el.get_attribute('href') for el in elements[num_links:]]
                all_links.extend(new_links)

                num_links = len(elements)

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

        return all_links


# for name, source in sources.items():
#     try:
#         all_links = []
#         scrapper = GAFAM_scrapper(source['link'],
#                                   source['by_1'],
#                                   source['button_element'],
#                                   source['by_2'],
#                                   source['article_element'])
#         driver = scrapper.start_driver()
#         all_links = scrapper.find_click_next_page(driver)
#         links_df = pd.DataFrame(all_links).drop_duplicates()
#         links_df.to_csv(f'{name}.csv')
#     except Exception as e:
#         print(f"Detected Ctrl+C! Saving data collected so far for {name}...")
#         links_df = pd.DataFrame(all_links).drop_duplicates()
#         links_df.to_csv(f'{name}_interrupted.csv')
#         print("Data saved. Exiting...")
#         break


def clean_text(text):
    pattern = r"Sign up for the weekly Amazon newsletter.*"

    cleaned_text = re.sub('\n', '', text.strip())
    cleaned_text = re.sub(pattern, '', cleaned_text)

    return cleaned_text


amazon_news = pd.read_csv('amazon_news_link.csv', index_col=0)
amazon_news = amazon_news.drop_duplicates()

scrapped_list = []
for link in amazon_news['0']:
    print(link)
    text = []

    r = requests.get(link)
    soup = BeautifulSoup(r.content, "html.parser")

    try:
        date_element = soup.find('div', ['PressReleasePage-dates'])
        date = re.findall('(?<=content=")(.*?)(?=T)', str(date_element))
    except TypeError:
        print('Could not collect date')
    try:
        article = soup.find('div', ['PressReleasePage-inner'])
        for item in article:
            text.append(item.get_text())
        text = clean_text(' '.join(text))
    except TypeError:
        print('Could not collect text')

    scrapped_list.append({'url': link,
                          'date': date,
                          'category': '---',
                          'text': text
                          })

scrapped_df = pd.DataFrame(scrapped_list)
scrapped_df.to_csv('amazon_news_text.csv')
