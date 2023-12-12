import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import time

import nltk
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from flair.models import TextClassifier
from flair.data import Sentence

from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from scipy.special import softmax

start_time = time.time()

"""
Twitter-roBERTa-base for Sentiment Analysis - UPDATED (2022):
https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest

XLM-T-Sent-Politics:
https://huggingface.co/cardiffnlp/xlm-twitter-politics-sentiment?text=Today%2C+the+promise+of+technology+to+help+us+solve+some+of+the+biggest+challenges+we+face+has+never+been+more+tangible%2C+and+nowhere+is+generative+AI+more+needed%2C+and+possibly+more+impactful%2C+than+in+healthcare.

Twitter-roBERTa-base for Sentiment Analysis
https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment?text=Today%2C+the+promise+of+technology+to+help+us+solve+some+of+the+biggest+challenges+we+face+has+never+been+more+tangible%2C+and+nowhere+is+generative+AI+more+needed%2C+and+possibly+more+impactful%2C+than+in+healthcare.
"""

nltk.download('punkt')

gafam = pd.read_csv('INCA_GAFAM_data.csv', index_col=0)
factiva = pd.read_csv('Factiva_part-000000000000.csv', low_memory=False)

combined_data = pd.concat([gafam['text'], factiva['body']]).reset_index(drop=True)


analyzer = SentimentIntensityAnalyzer()
flair_classifier = TextClassifier.load('en-sentiment')
MODEL = "cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
vectorizer = TfidfVectorizer()


def analyze_sentiment(sentences):
    vader_scores = {"neg": 0, "neu": 0, "pos": 0, "compound": 0}
    textblob_polarity = 0
    textblob_subjectivity = 0
    flair_scores = {"POSITIVE": 0, "NEGATIVE": 0}

    for sentence in sentences:
        v_score = analyzer.polarity_scores(sentence)
        for key in vader_scores:
            vader_scores[key] += v_score[key]

        tb_score = TextBlob(sentence).sentiment
        textblob_polarity += tb_score.polarity
        textblob_subjectivity += tb_score.subjectivity

        flair_sentence = Sentence(sentence)
        flair_classifier.predict(flair_sentence)
        flair_scores[flair_sentence.labels[0].value] += 1

    return vader_scores, textblob_polarity, textblob_subjectivity, flair_scores


def huggingface_sentiment(sentences):
    encoded_input = tokenizer(sentences, padding=True, truncation=True, return_tensors='pt')
    outputs = model(**encoded_input)
    scores = outputs.logits.detach().numpy()
    scores = softmax(scores, axis=1)
    return np.mean(scores, axis=0)


def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\w*\d\w*', '', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\u202f', ' ', text)
    text = re.sub(r'\xa0', ' ', text)
    text = re.sub(r'\s\s', ' ', text)
    return text


results = []
for number, text in enumerate(gafam.text):
    if not isinstance(text, str):
        continue

    print(f'Running sentiment analysis on {number+1} out of {len(combined_data)}')
    sentences = nltk.tokenize.sent_tokenize(text)
    preprocessed_text = [preprocess_text(sentence) for sentence in sentences]
    vectorizer.fit_transform(sentences)

    vader_scores, tb_polarity, tb_subjectivity, flair_scores = analyze_sentiment(sentences)
    try:
        hf_score = huggingface_sentiment(sentences)
    except RuntimeError as RE:
        print(RE, 'there is text format issue')


    results.append({
        'body': text,
        'vader_pos': vader_scores['pos'] / len(sentences),
        'vader_neu': vader_scores['neu'] / len(sentences),
        'vader_neg': vader_scores['neg'] / len(sentences),
        'vader_compound': vader_scores['compound'] / len(sentences),
        'textblob_polarity': tb_polarity / len(sentences),
        'textblob_subjectivity': tb_subjectivity / len(sentences),
        'flair_pos': flair_scores['POSITIVE'] / len(sentences),
        'flair_neg': flair_scores['NEGATIVE'] / len(sentences),
        'hf_pos': hf_score[2],
        'hf_neu': hf_score[1],
        'hf_neg': hf_score[0]
    })

df_results = pd.DataFrame(results)
merged_dfs = gafam.merge(df_results, on='text')

end_time = time.time()
print(f"Total time taken: {end_time - start_time} seconds")
