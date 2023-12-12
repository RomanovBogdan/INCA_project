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
    selenium_driver = webdriver.Chrome(service=service)
    selenium_driver.maximize_window()
    return selenium_driver


def collect_links(selenium_driver, url, by, article_element):
    selenium_driver.get(url)
    elements = selenium_driver.find_elements(by, article_element)
    article_links = [el.get_attribute('href') for el in elements]
    return article_links


def select_page(url_main_body, param_body, iterating_number):
    news_link = f'{url_main_body}{param_body}{iterating_number}/'
    return news_link


def convert_timestamp(date_obj_timestamp):
    dt_object = datetime.fromtimestamp(int(date_obj_timestamp), timezone.utc)
    return dt_object


def collect_text(beautiful_soup):
    entry_content = beautiful_soup.find("div", "entry-content")
    for i in entry_content.find_all('figure'):
        i.extract()

    for i in entry_content.find_all('p', 'tag-list'):
        i.extract()

    text_data_list = [i.get_text() for i in entry_content.find_all('p')]
    return text_data_list


def filter_text(text_data_list, phrases_to_remove_after):
    for i, text in enumerate(text_data_list):
        if any(phrase in text for phrase in phrases_to_remove_after):
            return text_data_list[:i]
    return text_data_list


def parse_datetime(s):
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return datetime.utcfromtimestamp(int(s))
        except ValueError:
            raise ValueError(f"Provided string '{s}' is neither a valid ISO 8601 string nor a Unix timestamp.")


main_body = 'https://news.microsoft.com/category/press-releases'
scraped_list = []
exceptions = ['100000-hours-over-skype-felicidades', 'oversight-board']

remove_phrases = [
    'For more information, ',
    'For further information',
    # "Editor’s note ",
    'About Microsoft',
    'Note to editors: '
    'Media Contacts',
    'Microsoft (Nasdaq “MSFT” @microsoft)'
]

last_page = 1036
driver = start_driver()

for page_number in range(143, last_page):
    # max(last_page) == 1035
    print(f"Processing page {page_number} of {last_page - 1}...")

    webpage = select_page(main_body, '/page/', page_number)
    links = collect_links(driver, webpage, By.CLASS_NAME, 'f-post-link')

    for link_number, link in enumerate(links):
        if any(except_part in link for except_part in exceptions):
            title = '-'
            date = '-'
            text_list = []
            print('Skype happened')
            continue

        else:
            driver.get(link)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')

            message = soup.find('p').get_text()

            if 'too many times' not in message:
                date_timestamp = soup.find("time")['datetime']
                date = parse_datetime(date_timestamp)

                title = soup.find("h1", "entry-title").get_text()

                summary = ' '
                try:
                    summary = soup.find('h3').get_text() + ' '
                except AttributeError:
                    print('\t--There is no summary section')

                text_list = collect_text(soup)
                text_list.insert(0, summary)

        scraped_list.append({'url': link,
                             'title': title,
                             'date': date,
                             'text': ' '.join(text_list),
                             'sorted_text': ' '.join(filter_text(text_list, remove_phrases))
                             })

        time.sleep(random.randint(1, 2))
        print(f"\tProcessed link {link_number+1} of {len(links)} on page {page_number}.")

scraped_df = pd.DataFrame(scraped_list)
scraped_df.to_csv('./new_INCA_data/MicrosoftNews_data.csv')
scraped_df.shape