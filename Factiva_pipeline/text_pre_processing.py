import spacy

# you should pre-install the `en_core_web_sm` model before loading it
# python3 -m spacy download en_core_web_sm
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
    # Parse the sentence using the loaded 'en_core_web_sm' model object `nlp`
    file = nlp(text)

    # Extract the lemma for each token and join
    lemmatized_text = " ".join([token.lemma_ for token in file if token.pos_ in ["NOUN", "VERB", "ADJ"]])
    return lemmatized_text

text = "INCA, 'Increase corporate political responsibility and accountability', investigates the impact " \
       "that digital platforms have on European democracies and institutions"
cleaned_text = clean_text(text)
print(cleaned_text)
