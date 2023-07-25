import pandas as pd
import dl_translate as dlt
import nltk
import pycountry
from tqdm import tqdm
import re

df = pd.read_csv('first_extract_clean.csv')

mt = dlt.TranslationModel("facebook/nllb-200-distilled-600M")

texts = pd.DataFrame(df['text'])

# Language detection

def get_language_name(code):
    try:
        lang = pycountry.languages.get(alpha_2=code)
        return lang.name
    except AttributeError:
        try:
            lang = pycountry.languages.get(alpha_3=code)
            return lang.name
        except AttributeError:
            return "unknown"

texts['iso_code'] = df['lang']
texts['full_lang'] = [get_language_name(iso_code) for iso_code in texts['iso_code']]

# Text cleaning

texts['text'] = [re.sub('\\n', ' ', str(i)) for i in texts['text']]
texts['text'] = [re.sub('\s+', ' ', str(i)) for i in texts['text']]

# Translation

texts_translation = []

# texts.shape[0]

for i in tqdm(range(texts.shape[0])):
    text_language = texts.loc[i, 'full_lang']
    # If in English, not translation needed
    if text_language == 'English':
        texts_translation.append(texts.text[i])
    else:
        if text_language == 'Bulgarian':
            sents = nltk.tokenize.sent_tokenize(texts.text[i])
        else:
            sents = nltk.tokenize.sent_tokenize(texts.text[i], text_language)
        sents_trans = " ".join(mt.translate(sents, source=text_language, target=dlt.lang.ENGLISH, generation_options=dict(max_new_tokens=1024), batch_size=32))
        texts_translation.append(sents_trans)

