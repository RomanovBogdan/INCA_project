import pandas as pd
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC

links = []
gafam = ['Google', 'Facebook', 'Amazon', 'Apple', 'Microsoft']

for company in gafam:
    url = f"https://yle-fi-search.api.yle.fi/v1/search?app_id=hakuylefi_v2_prod&" \
          f"app_key=4c1422b466ee676e03c4ba9866c0921f&language=fi&limit=1200&offset=0&query={company}&type=article"

    response = requests.get(url)
    data_str = response.text
    print(len(data_str))
    data_json = json.loads(data_str)
    for element in data_json['data']:
        print(element['url']['full'])
        links.append({'platform': company,
                      'publication_date': element['datePublished'],
                      'long_url': element['url']['full']})

links_df = pd.DataFrame(links)

def start_driver():
    chrome_options = Options()

    chrome_driver_path = './chromedriver-mac-arm64/chromedriver'
    service = Service(executable_path=chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()
    return driver


driver = start_driver()
driver.get(links_df['long_url'][0])
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, 'ycd-consent-buttons__button'))
).click()

texts = []
error_links = []
for number, link in enumerate(links_df['long_url']):
    driver.get(link)

    try:
        print(f"This is link number {number} of out {len(links_df['long_url'])}")
        WebDriverWait(driver, 2)
        title = driver.find_element(By.XPATH,
                                    '//*[@id="yle__contentAnchor"]/div[1]/main/div[1]/div/article/header/h1').text
        abstract = driver.find_element(By.XPATH,
                                       '//*[@id="yle__contentAnchor"]/div[1]/main/div[1]/div/article/header/p').text
        article = driver.find_element(By.CLASS_NAME, 'yle__article__content').text

        texts.append({
            'long_url': link,
            'article_text': title + ' ' + abstract + ' ' + article
        })
    except Exception as E:
        print(f'There is an error in link {link}')
        error_links.append(link)
        continue

texts_df = pd.DataFrame(texts)
errors_df = pd.DataFrame(error_links)

final_df = links_df.merge(texts_df, on='long_url', how='left')
final_df = final_df.drop_duplicates().dropna()

final_df.to_csv('gafam_finnish_news_text.csv')
errors_df.to_csv('errors_links.csv')
