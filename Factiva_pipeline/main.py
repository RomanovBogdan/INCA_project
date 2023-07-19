import pandas as pd
import dl_translate as dlt
import nltk
import ssl
from langdetect import detect
import pycountry

# nltk.download
# nltk.download('punkt')
FACTIVA_FILE_PATH = ''

class LanguageProcessing:

    def __init__(self, json_file):
        self.json_file = json_file
        self.texts = None
        self.mt = dlt.TranslationModel()

    @staticmethod
    def _create_ssl_context():
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

    @staticmethod
    def define_iso_code(texts):
        lang_list = []
        for text in texts:
            try:
                lang = detect(text)
                lang_list.append(lang)
            except:
                lang_list.append('unknown')
        return lang_list

    @staticmethod
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

    def translate_sentences(self, sents, source_lang_attr, max_length=1024):
        return " ".join(self.mt.translate(sents,
                                          source=source_lang_attr,
                                          target=dlt.lang.ENGLISH,
                                          generation_options=dict(max_length=max_length)))

    def process_texts(self):
        self._create_ssl_context()
        df = pd.read_json(self.json_file, lines=True)
        self.texts = pd.DataFrame(df['body'])
        self.texts['iso_code'] = self.define_iso_code(self.texts.body)
        self.texts['full_lang'] = [self.get_language_name(iso_code) for iso_code in self.texts['iso_code']]
        self.texts.dropna(subset=['body'], inplace=True)
        self.texts.reset_index(inplace=True, drop=True)

    def translate_texts(self):
        texts_translation = []
        for row in self.texts.loc[:1, :].iterrows():
            sents = nltk.tokenize.sent_tokenize(row[1][0], row[1][2])
            print('one sentence is done')
            translated_text = self.translate_sentences(sents, row[1][2])
            texts_translation.append(translated_text)
        return texts_translation


processor = LanguageProcessing(FACTIVA_FILE_PATH)
processor.process_texts()
df = processor.texts
print('Processing is done')

translations = processor.translate_texts()
