import fitz
import pandas as pd
import os
import re
import warnings
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import gensim
from gensim.models import Phrases
from gensim.models.phrases import Phraser
import spacy
from gensim import corpora
import pyLDAvis
import pyLDAvis.gensim
import matplotlib.pyplot as plt
import webbrowser

warnings.filterwarnings("ignore", category=DeprecationWarning)

nltk.download('stopwords')
nltk.download('punkt')

stop_words = stopwords.words('english')
stop_words.extend(['from', 'subject', 're', 'edu', 'use'])

nlp = spacy.load('en_core_web_sm', disable=['parser','ner'])

def extract_text_from_pdf(pdf_path):
    text = ""
    pdf_document = fitz.open(pdf_path)
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        text += page.get_text()
    pdf_document.close()

    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'[^A-Za-z\s]+', ' ', text).lower()

    return text

def lemmatization(texts, tags=['NOUN', 'ADJ', 'VERB', 'ADV', 'PROPN']):
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent))
        texts_out.append([token.lemma_ for token in doc if token.pos_ in tags])
    return texts_out

pdf_paths = [
    'C:/Users/amits/Downloads/Threat Intelligence Reports/moveit-containment-hardening-guide-rpt-en.pdf',
    'C:/Users/amits/Downloads/Threat Intelligence Reports/rpt-dll-sideloading.pdf',
    'C:/Users/amits/Downloads/Threat Intelligence Reports/rpt-apt29-hammertoss-stealthy-tactics-define-en.pdf',
    'C:/Users/amits/Downloads/Threat Intelligence Reports/barracuda-esg-rpt-en.pdf',
    # Add more PDF paths as needed
]

all_text = ""
for pdf_path in pdf_paths:
    all_text += extract_text_from_pdf(pdf_path) + " "

filtered_text = ' '.join([word for word in word_tokenize(all_text) if word not in stop_words and len(word) > 2])
sentences = [word_tokenize(sentence) for sentence in filtered_text.split('.')]
bigram = Phrases(sentences, min_count=5, threshold=100)
trigram = Phrases(bigram[sentences], threshold=100)
bigram_phraser = Phraser(bigram)
trigram_phraser = Phraser(trigram)
bow = [trigram_phraser[bigram_phraser[sentence]] for sentence in sentences]
bag_of_words = lemmatization(bow)
id2word = corpora.Dictionary(bag_of_words)
corpus_matrix = [id2word.doc2bow(sent) for sent in bag_of_words]
print(corpus_matrix)
lda_model = gensim.models.ldamodel.LdaModel(corpus=corpus_matrix, id2word=id2word, num_topics=20, random_state=100, update_every=1, chunksize=100, passes=5, alpha='auto', per_word_topics=True)

# Create a visualization for all topics
vis = pyLDAvis.gensim.prepare(lda_model, corpus=corpus_matrix, dictionary=id2word)
html_path = 'lda_vis.html'
pyLDAvis.save_html(vis, html_path)

if os.path.exists(html_path):
    webbrowser.open(f'file://{os.path.abspath(html_path)}')
else:
    print(f"Error: File '{html_path}' not found.")
