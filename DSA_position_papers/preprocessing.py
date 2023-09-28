from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import pandas as pd
import re
import string

df = pd.read_csv('DSA_DMA_position_paper_improved.csv', index_col=0)

english_stopwords = set(stopwords.words('english'))
english_words = set(words.words())
lemmatizer = WordNetLemmatizer()


def remove_urls(text):
    url_pattern = re.compile(r'\b(?:http[s]?://)?\S+\.\S+')
    return url_pattern.sub('', text)


def remove_numbers(text):
    return re.sub(r'\d+', '', text)


def remove_letters(text):
    return re.sub(r'[a-zA-Z]', '', text)


def get_additional_punctuation(dataframe, column_with_text):
    all_texts = ' '.join(dataframe[column_with_text])
    additional_punctuation = set(remove_letters(all_texts))
    for new_punctuation in additional_punctuation:
        string.punctuation = string.punctuation + str(new_punctuation.strip())


def remove_punctuation(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.translate(translator)


def remove_whitespace(text):
    return " ".join(text.split())


def tokenization_stopwords(text):
    tokens = word_tokenize(text.lower())
    return [token for token in tokens if token not in english_stopwords]


def lemmatization(tokens):
    return ' '.join(lemmatizer.lemmatize(token) for token in tokens)


def keep_english_words(text):
    return ' '.join(word for word in text.split() if word in english_words)


def preprocess_text(text):
    text = remove_urls(text)
    text = remove_numbers(text)
    text = remove_punctuation(text)
    text = remove_whitespace(text)
    tokens = tokenization_stopwords(text)

    return lemmatization(tokens)


get_additional_punctuation(df, 'text')
df['preprocessed_data'] = df['text'].apply(preprocess_text)

# df.drop(columns=['method', 'len']).to_csv('DSA_DMA_preprocessed_data.csv')
