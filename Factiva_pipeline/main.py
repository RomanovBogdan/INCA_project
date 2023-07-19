import pandas as pd
import dl_translate as dlt
import nltk
import ssl
from langdetect import detect
import pycountry


try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def define_iso_code(texts):
    lang_list = []
    for text in texts:
        try:
            lang = detect(text)
            lang_list.append(lang)
        except:
            lang_list.append('unknown')
    return lang_list

def get_language_name(code):
    try:
        lang = pycountry.languages.get(alpha_2=code) # for ISO 639-1 language codes
        return lang.name
    except AttributeError:
        try:
            lang = pycountry.languages.get(alpha_3=code) # for ISO 639-2/3 language codes
            return lang.name
        except AttributeError:
            return "unknown"

# def translate_sentences(sents, source_lang, max_length):
#     return " ".join(mt.translate(sents, source=source_lang,
#                                  target=dlt.lang.ENGLISH,
#                                  generation_options=dict(max_length=max_length)))

def translate_sentences(sents, source_lang_attr, max_length):
    source_lang = getattr(dlt.lang, source_lang_attr.split(".")[-1])
    return " ".join(mt.translate(sents, source=source_lang,
                                 target=dlt.lang.ENGLISH,
                                 generation_options=dict(max_length=max_length)))


nltk.download
nltk.download('punkt')

df = pd.read_json('Factiva_pipeline/part-000000000000.json', lines=True)
texts = pd.DataFrame(df['body'])
print('Separated texts')
texts['iso_code'] = define_iso_code(texts.body)
texts['full_lang'] = [get_language_name(iso_code) for iso_code in texts['iso_code']]
texts['full_lang_caps'] = [lang.upper() for lang in texts['full_lang']]
texts.dropna(subset=['body'], inplace=True)
texts.reset_index(inplace=True, drop=True)
print('Prepared texts for translation')

mt = dlt.TranslationModel()
texts_translation = []
for row in texts[:3].iterrows():
    sents = nltk.tokenize.sent_tokenize(row[1][0], row[1][2])
    translated_sent = mt.translate(sents, source=dlt.lang.ENGLISH,
                                     target=dlt.lang.RUSSIAN,
                                     generation_options=dict(max_length=1024))
    print(translated_sent)
    translated_text = " ".join(translated_sent)
    # test = translate_sentences(sents, row[1][3], 1024)
    texts_translation.append(translated_text)

