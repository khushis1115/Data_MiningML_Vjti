import requests
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import re
import spacy
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os
from tensorflow.keras.preprocessing.sequence import pad_sequences

nlpPreprocess = spacy.load("en_core_web_sm")

# Choose a valid sentence-transformers model
sbert_model = SentenceTransformer("all-MiniLM-L6-v2")  # Example of a valid model

def read_pdf_from_url(pdf_url):
    # Download the PDF file from the URL
    response = requests.get(pdf_url)

    try:
        with open('downloaded_pdf.pdf', 'wb') as pdf_file:
            pdf_file.write(response.content)

        # Read the text from the downloaded PDF file
        with open('downloaded_pdf.pdf', 'rb') as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)

            text = ''
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + " \n "

    except:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text(strip=True, separator=". \n ")

    return text.replace("\n", " \n ")

def CleanText(text):
    cleaned_text = re.sub(r'\s+', ' ', text)  # remove blank spaces
    cleaned_text = re.sub(r'[^a-zA-Z0-9\s.,!?:/()\[\]@_-]+', '', cleaned_text)  # keep only required characters
    return cleaned_text

def partition_text_by_topic(doc):
    # Initialize a list to store the indices of topic changes
    topic_change_indices = [0]

    # Iterate through sentences to identify topic changes
    for i in range(1, len(list(doc.sents))):
        prev_sentence = list(doc.sents)[i - 1]
        current_sentence = list(doc.sents)[i]

        # Extract named entities from the previous and current sentences
        prev_entities = {ent.text.lower() for ent in prev_sentence.ents}
        current_entities = {ent.text.lower() for ent in current_sentence.ents}

        # Check for changes in named entities
        if not prev_entities.intersection(current_entities):
            # Add the index of the current sentence as a potential topic change
            topic_change_indices.append(i)

    TopicSplittedTexts = []
    # Optionally, print the sentences between detected topic changes
    for i in range(len(topic_change_indices) - 1):
        start_index = topic_change_indices[i]
        end_index = topic_change_indices[i + 1]
        topic_chunk = list(doc.sents)[start_index:end_index]
        TopicSplittedTexts.append(' '.join(map(str, topic_chunk)))

    return TopicSplittedTexts

def TextToChunks(URL):  # using spacy
    text = read_pdf_from_url(URL)
    Chean_Text = CleanText(text)
    SpacyTexts = nlpPreprocess(text)  # convert text into spacy text    # spacy = nlp library
    Chunks = []
    sentences = []

    for i in SpacyTexts.sents:
        sentences.append(i)

    Chunks = partition_text_by_topic(SpacyTexts)
    return Chunks, sentences, SpacyTexts

# Extract text from the provided PDF URL
# pdf_url = "https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2023/11/09055246/Modern-Asian-APT-groups-TTPs_report_eng.pdf"     #securelist report used in TIM
pdf_url = "/content/aa23-129a_snake_malware_2.pdf"

Chunks, Sentences, SpacyTexts = TextToChunks(pdf_url)
Chunks

import TTPelement
# elems, count, replaced = TTPelement.GetTTPelements(Chunks[22])
# dict of ttp elements, count vector of elements, the string converted to lower and replaced with keywords
def GetTTPElementsFromChunks(Chunks):  # window size 3 text
    Elements = []
    Count = []
    Replaced = []

    for i in Chunks:
        elems, count, replaced = TTPelement.GetTTPelements(i)
        Elements.append(elems)
        Count.append(count)
        Replaced.append(replaced)

    return Elements, Count, Replaced

ELEMENTS, COUNTS, CHUNKSREPLACED = GetTTPElementsFromChunks(Chunks)
ELEMENTS  # adhi to
COUNTS
CHUNKSREPLACED
Embeddings = sbert_model.encode(CHUNKSREPLACED)
Embeddings

with open('/content/drive/MyDrive/TTPcorrelationProjectFiles/LSTM.pkl', 'rb') as file:
    model = pickle.load(file)

with open('/content/drive/MyDrive/TTPcorrelationProjectFiles/LabelEncoder.pkl', 'rb') as file:
    le = pickle.load(file)

with open('/content/drive/MyDrive/TTPcorrelationProjectFiles/Tokenizer.pkl', 'rb') as file:
    tokenizer = pickle.load(file)

with open('/content/drive/MyDrive/TTPcorrelationProjectFiles/TacticMap.pkl', 'rb') as file:
    TacticMapping = pickle.load(file)

with open('/content/drive/MyDrive/TTPcorrelationProjectFiles/TechniqueMap.pkl', 'rb') as file:
    TechniqueMapping = pickle.load(file)

sequences = tokenizer.texts_to_sequences(CHUNKSREPLACED)
# Padding sequences
X_test_padded = pad_sequences(sequences)
LSTMPred = model.predict(X_test_padded)
LSTMpredicted_classes = np.argmax(LSTMPred, axis=1)

Cat_Pred = le.inverse_transform(LSTMpredicted_classes)

TacticNames = []
techniqueNames = []

for i in Cat_Pred:
    TacticNames.append(TacticMapping[i])
    techniqueNames.append(TechniqueMapping[i])
