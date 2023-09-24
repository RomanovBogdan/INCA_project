from nltk.corpus import stopwords, words
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import pandas as pd
import re
import string

df = pd.read_csv('DSA_position_paper_improved.csv', index_col=0)

english_stopwords = set(stopwords.words('english'))
english_words = set(words.words())


def remove_numbers(text):
    return re.sub(r'\d+', '', text)

def remove_urls(text):
    url_pattern = re.compile(r'\b(?:http[s]?://)?\S+\.\S+')
    return url_pattern.sub('', text)


def remove_letters(text):
    return re.sub(r'[a-zA-Z]', '', text)

def generate_new_punctuation(dataframe, column_with_text):
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

def keep_english_words(text):
    return ' '.join(word for word in text.split() if word in english_words)


def lemmatization(tokens):
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in tokens]
    return ' '.join(lemmatized_tokens)


def preprocess_text(text):
    cleaned_text = remove_urls(text)

    cleaned_text = remove_numbers(cleaned_text)

    cleaned_text = remove_punctuation(cleaned_text)

    cleaned_text = remove_whitespace(cleaned_text)

    cleaned_tokens = tokenization_stopwords(cleaned_text)

    processed_text = lemmatization(cleaned_tokens)

    return processed_text

generate_new_punctuation(df, 'text')

df['cleaned_text'] = df['text'].apply(preprocess_text)

df.drop(columns=['method', 'len']).to_csv('preprocessed_data.csv')