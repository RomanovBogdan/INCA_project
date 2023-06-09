import re
import pandas as pd
import requests
from bs4 import BeautifulSoup


class ScrapperWithPageNum:
    def __init__(self, main_body):
        self.main_body = main_body

    def select_page(self, param_body, i):
        news_link = f'{self.main_body}{param_body}{i}'
        print(news_link)
        r = requests.get(news_link)
        soup = BeautifulSoup(r.content, 'html.parser')

        return soup

    @staticmethod
    def collect_links(soup, element, html_class):
        article_element = soup.find(element, html_class)
        a_tags = article_element.find_all('a')
        links = [tag.get('href') for tag in a_tags]

        return links

    @staticmethod
    def collect_date(content, element, date_element):
        return content.find(element, date_element).get_text()

    @staticmethod
    def collect_category(content, element, category_element):  # category-eyebrow__
        return content.find(element, class_=re.compile(f'^{category_element}')).get_text()

    @staticmethod
    def collect_text(content, element, text_element1, text_element2):
        # div, 'hero-headline', 'pagebody text component'
        return content.find(element, [text_element1, text_element2]).get_text()

    def collect_content(self, link, article_element):
        page_link = f'{self.main_body}{link}'
        r = requests.get(page_link)
        soup = BeautifulSoup(r.content, 'html.parser')
        content = soup.find(article_element)

        return content


scrapper = ScrapperWithPageNum('https://www.apple.com/')
info_list = []
for i in range(1, 4):
    soup = scrapper.select_page('/newsroom/archive/?page=', i)
    links = scrapper.collect_links(soup, 'div', 'results')
    for link in links:
        content = scrapper.collect_content(link, 'article')
        date = scrapper.collect_date(content, 'span', 'category-eyebrow__date')
        category = scrapper.collect_category(content, 'span', 'category-eyebrow__')
        text = scrapper.collect_text(content, 'div', 'hero-headline', 'pagebody text component')

        info_list.append({'url': link,
                          'date': date,
                          'category': category,
                          'text': text
                          })

test = pd.DataFrame(info_list)
# test.to_csv('apple_newsroom_text.csv')
