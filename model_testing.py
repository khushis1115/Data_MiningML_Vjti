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
import time
from tensorflow.keras.preprocessing.sequence import pad_sequences
from stix2 import Indicator, Relationship, Report, AttackPattern, Bundle
import json



Num_Classes = 267

nlpPreprocess = spacy.load("en_core_web_sm")

#sbert_model = SentenceTransformer("jackaduma/SecBERT")

from google.colab import drive
drive.mount('/content/drive/')

import sys
sys.path.append('/content/drive/MyDrive/TTPcorrelationProjectFiles')

import TTPelement

with open('C:/Users/amits/Downloads/Pickle-20240612T080633Z-001/Pickle/LSTM.pkl', 'rb') as file:
    model = pickle.load(file)

with open('C:/Users/amits/Downloads/Pickle-20240612T080633Z-001/Pickle/LabelEncoder.pkl', 'rb') as file:
    le = pickle.load(file)

with open('C:/Users/amits/Downloads/Pickle-20240612T080633Z-001/Pickle/Tokenizer.pkl', 'rb') as file:
    tokenizer = pickle.load(file)

with open('C:/Users/amits/Downloads/Pickle-20240612T080633Z-001/Pickle/TacticMap.pkl', 'rb') as file:
    TacticMapping = pickle.load(file)

with open('C:/Users/amits/Downloads/Pickle-20240612T080633Z-001/Pickle/TechniqueMap.pkl', 'rb') as file:
    TechniqueMapping = pickle.load(file)





"""# **Document Crawling**"""





def read_pdf_from_url(pdf_url):
    # Download the PDF file from the URL

    response = requests.get(pdf_url)

    try:
      with open('downloaded_pdf.pdf', 'wb') as pdf_file:
        pdf_file.write(response.content)

      # Read the text from the downloaded PDF files
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

def read_pdf_from_url(pdf_url):      # read downloaded file

  with open(pdf_url, 'rb') as file:
    pdf_reader = PdfReader(file)
    num_pages = len(pdf_reader.pages)

    text = ''
    for page_num in range(num_pages):
      page = pdf_reader.pages[page_num]
      text += page.extract_text() + " \n "

    return text.replace("\n", " \n ")



"""# **Preprocessing**"""

def CleanMyText(text):
  cleaned_text = re.sub(r'\s+', ' ', text)    # remove blank spaces
  cleaned_text = re.sub(r'[^a-zA-Z0-9\s.,!?:/()\[\]@_-]+', '', cleaned_text)     # keep only required characters

  return cleaned_text

#Sent 1,  Sent 2,  Sent 3, Sent 4      sentence split using NER
#jera    jera       tf     jera

"""# **Dynamic Text Splitting by NER**"""

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

    print(TopicSplittedTexts)

    return TopicSplittedTexts



def TextToChunks(URL):      #  using spacy

  text = read_pdf_from_url(URL)

  Chean_Text = CleanMyText(text)

  SpacyTexts = nlpPreprocess(text)    # convert text into spacy text    # spacy = nlp library


  Chunks = []
  sentences = []

  for i in SpacyTexts.sents:
    sentences.append(i)


    Chunks = partition_text_by_topic(SpacyTexts)

  return Chunks, sentences, SpacyTexts, Chean_Text

# topic chunk 1,   topic chunk 2,    topic chunk 3

#    my address is 122.19.0.1
#    mu address is ipv4        pass to classifier


"""
{
  ipv4: [192.165.0.2, 182,... ],
  url: []
  hash: []



}
"""

"""# **TTP elements extraction and relacement**"""

def GetTTPElementsFromChunks( Chunks ):

  Elements = []
  Count = []
  Replaced = []

  for i in Chunks:
    elems, count, replaced = TTPelement.GetTTPelements(i)

    Elements.append(elems)
    Count.append(count)
    Replaced.append(replaced)

  return Elements, Count, Replaced



"""# **Transformer**"""

#Embeddings = sbert_model.encode(CHUNKSREPLACED)

#Embeddings

"""# **Classifier**"""

def GetLSTMoutput(Chunks):

  sequences = tokenizer.texts_to_sequences(Chunks)

  # Padding sequences
  X_test_padded = pad_sequences(sequences)

  LSTMPred = model.predict(X_test_padded)

  return LSTMPred

"""T = [0.2, 0.4 ,0.5, 0.3]

Ou= [0.30,0.45,0.1,0.25 ]     #   0.45, 0.30, 0.25, 0.1
(p,i)
"""

Thresholds = [0.0173, 0.2366, 0.1833, 0.1159, 0.0134, 0.1527, 0.5134, 0.0442,
       0.2612, 0.2414, 0.0276, 0.0341, 0.0276, 0.0611, 0.1593, 0.2092,
       0.0096, 0.0932, 0.0278, 0.0343, 0.0223, 0.0967, 0.077 , 0.1831,
       0.0557, 0.1873, 0.1538, 0.956 , 0.0477, 0.0051, 0.9863, 0.1389,
       0.0288, 0.0286, 0.1198, 0.0838, 0.0347, 0.0044, 0.0161, 0.0964,
       0.0233, 0.0768, 0.0874, 0.0078, 0.9768, 0.1408, 0.4197, 0.2594,
       0.2836, 0.0642, 0.244 , 0.4173, 0.0684, 0.121 , 0.0165, 0.3374,
       0.5935, 0.034 , 0.7427, 0.228 , 0.5228, 0.0987, 0.1082, 0.0229,
       0.4995, 0.2831, 0.0782, 0.0249, 0.1602, 0.0442, 0.0604, 0.0678,
       0.0402, 0.4758, 0.0233, 0.0711, 0.2678, 0.1268, 0.1174, 0.0438,
       0.019 , 0.0271, 0.1159, 0.4535, 0.0328, 0.0403, 0.0226, 0.0481,
       0.0384, 0.2161, 0.1017, 0.1177, 0.0175, 0.0617, 0.0133, 0.0366,
       0.0473, 0.4033, 0.0671, 0.0107, 0.0547, 0.0265, 0.0451, 0.0141,
       0.0965, 0.2163, 0.0108, 0.0475, 0.0131, 0.1003, 0.0363, 0.4207,
       0.1235, 0.3248, 0.0196, 0.018 , 0.0183, 0.0651, 0.0577, 0.0325,
       0.0894, 0.0268, 0.0999, 0.0023, 0.0055, 0.0675, 0.1011, 0.0181,
       0.0108, 0.4179, 0.0149, 0.0203, 0.0683, 0.0079, 0.0392, 0.0264,
       0.1832, 0.0579, 0.1417, 0.0505, 0.0514, 0.0388, 0.0411, 0.026 ,
       0.1436, 0.0905, 0.0524, 0.0338, 0.0096, 0.1828, 0.054 , 0.2722,
       0.0163, 0.7344, 0.0699, 0.0614, 0.0572, 0.0831, 0.073 , 0.1157,
       0.0418, 0.0286, 0.0544, 0.0151, 0.3873, 0.2625, 0.0711, 0.1092,
       0.664 , 0.4956, 0.0927, 0.2183, 0.0584, 0.0863, 0.5684, 0.3111,
       0.1154, 0.0375, 0.0302, 0.3857, 0.0258, 0.249 , 0.0355, 0.1206,
       0.1291, 0.8804, 0.026 , 0.0343, 0.2551, 0.1227, 0.0329, 0.1254,
       0.6572, 0.6714, 0.2236, 0.0195, 0.0176, 0.0291, 0.0723, 0.5397,
       0.0259, 0.0689, 0.192 , 0.1136, 0.0761, 0.0555, 0.1797, 0.0173,
       0.0733, 0.1069, 0.0827, 0.1649, 0.0291, 0.0624, 0.0121, 0.1527,
       0.0259, 0.0462, 0.5058, 0.1308, 0.0236, 0.1346, 0.1054, 0.0075,
       0.2323, 0.0329, 0.0714, 0.0347, 0.082 , 0.0227, 0.0934, 0.2367,
       0.0349, 0.0615, 0.0287, 0.0472, 0.0844, 0.1472, 0.0257, 0.08  ,
       0.0177, 0.0429, 0.1637, 0.7957, 0.0247, 0.0099, 0.0324, 0.012 ,
       0.0346, 0.1116, 0.0377, 0.0197, 0.2971, 0.0476, 0.015 , 0.0604,
       0.0484, 0.0626, 0.0536, 0.0421, 0.0419, 0.0285, 0.03  , 0.2443,
       0.0335, 0.0555, 0.0362]





def GetClassPreds(lstmOut, Threshol):

  """ArgIndexes = np.zeros( len(Threshol),dtype = int )
  LSTMpredicted_classes = np.zeros(lstmOut.shape[0])
  SortedIndexes = lstmOut.argsort(axis = 1)

  NoClasses = []

  for i in range(0, len(SortedIndexes)):

    Desc = np.flip(SortedIndexes[i])

    for j in range(0,Num_Classes):
      ArgIndexes[ Desc[j] ] = j

    for j in ArgIndexes:

      if lstmOut[i][j] >= Threshol[j]:
        LSTMpredicted_classes[i] = j
        break
    else:
      LSTMpredicted_classes[i] = 0 #   will be changed to "No Class" later
      NoClasses.append(i)

  LSTMpredicted_classes = np.array(LSTMpredicted_classes, dtype = int)

  Cat_Pred = le.inverse_transform(LSTMpredicted_classes)

  for i in NoClasses: Cat_Pred[i] = "No Class"
  """

  NoClasses = []

  Classes = []


  for i in range(0,len(lstmOut)):
    # i = cur_Prob

    NeededIndex = np.argmax(lstmOut[i])

    if lstmOut[i][NeededIndex] >= Threshol[NeededIndex]:
      Classes.append(NeededIndex)
    else:
      Classes.append(0)
      NoClasses.append(i)

  Cat_Pred = le.inverse_transform(Classes)

  for i in NoClasses: Cat_Pred[i] = "No Class"


  return Cat_Pred





"""# Tactic and Technique mapping"""



def GetCTacticTechniqueName(Category_pred):
  TacticNames = []
  techniqueNames = []

  for i in Category_pred:
    TacticNames.append(TacticMapping[i])
    techniqueNames.append(TechniqueMapping[i])

  return TacticNames, techniqueNames

#    topic chunk, IOC, Class, TacticNames, techniqueNames

#   chunk, Class, TacticNames, techniqueNames    ->   attack pattern
#   IOC  -> indicator

"""# STIX file generation"""



def CreateStixIndicator(IOCtype,IOCvalue):

  if IOCtype == r"ipv4": patternVal = "[ipv4-addr:value = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == "ipv6": patternVal = "[ipv6-addr:value = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"asn": patternVal = "[autonomous-system:number = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"domain": patternVal = "[domain-name:value = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"email": patternVal = "[email-addr:value = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"filename": patternVal = "[file:name = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"url": patternVal = "[url:value = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"hash": patternVal = "[file:hash = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"filepath": patternVal = "[file:file_path = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"cve": patternVal = "[vulnerability:cve = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"regkey": patternVal = "[windows-registry-key:key = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"encodeencryptalgorithms": patternVal = "[crypto-algorithm:name = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"communicationprotocol": patternVal = "[network-traffic:protocols[*] = '{}']".format(IOCvalue.replace('\\','/'))
  elif IOCtype == r"dataobject": patternVal = "[artifact:payload_bin = '{}']".format(IOCvalue.replace('\\','/'))

  indicator = Indicator(
    name=IOCtype,
    description="Extracted " + IOCtype,
    indicator_types=["malicious-activity"],
    pattern= patternVal ,
    labels=["malicious"],
    pattern_type="stix"
    )

  return indicator





def ReturnStixObjects(counts, Pred_cat, TechName, tacName, ReplChunk, elems, DoIncludeNonIOC = False):

  IndicatorsSTIX = []
  RelationshipSTIX = []
  AttackPatternSTIX = []

  for i in range(0,len(counts)):
    if counts[i].sum() and Pred_cat[i] != "No Class":

      attack_pattern = AttackPattern(
          name = TechName[i],
          description = ReplChunk[i],
          custom_properties = {"tactic_name": tacName[i], "ttp_id": Pred_cat[i] },
          allow_custom=True
          )

      AttackPatternSTIX.append(attack_pattern)


      for j in elems[i]:


        if len(elems[i][j]):

          for iocs in elems[i][j]:

            indicator = CreateStixIndicator(j,str(iocs))
            IndicatorsSTIX.append(indicator)


            relationship_indicator_attack_pattern = Relationship(
                source_ref=indicator.id,
                target_ref=attack_pattern.id,
                relationship_type="indicates",
                )
            RelationshipSTIX.append(relationship_indicator_attack_pattern)

    elif DoIncludeNonIOC and Pred_cat[i] != "No Class":

      attack_pattern = AttackPattern(
          name = TechName[i],
          description = ReplChunk[i],
          custom_properties = {"tactic_name": tacName[i], "ttp_id": Pred_cat[i] },
          allow_custom=True
          )

      AttackPatternSTIX.append(attack_pattern)

  return IndicatorsSTIX, RelationshipSTIX, AttackPatternSTIX





def MakeStix(Indicators, Relationships, AttcakPatterns, CleanText, ReportName):

  AllIDs = []

  for i in Indicators: AllIDs.append(i.id)

  for i in Relationships: AllIDs.append(i.id)

  for i in AttcakPatterns: AllIDs.append(i.id)

  report = Report(
      name= ReportName,
      description=CleanText,
      published="2024-02-18T00:00:00Z",
      object_refs=AllIDs,
      )

  Objects = Indicators + AttcakPatterns + [report] + Relationships

  # Create a bundle
  bundle = Bundle(objects= Objects ,allow_custom=True)

  with open( ReportName + ".json", "w") as f:
    json.dump(json.loads(bundle.serialize()), f, indent=4)







"""# Main function"""

def MainFunction(PdfLink, OutputDirectory = ""):

  Chunks, Sentences, SpacyTexts, CleanText = TextToChunks(PdfLink)
  ELEMENTS, COUNTS, CHUNKSREPLACED = GetTTPElementsFromChunks( Chunks )
  COUNTS = np.array(COUNTS)
  LSTMPred = GetLSTMoutput( CHUNKSREPLACED )
  Cat_Pred = GetClassPreds(LSTMPred, Thresholds)
  TacticNames,techniqueNames = GetCTacticTechniqueName(Cat_Pred)
  IndicatorsSTIX, RelationshipSTIX, AttackPatternSTIX = ReturnStixObjects(COUNTS,Cat_Pred, techniqueNames, TacticNames, CHUNKSREPLACED, ELEMENTS)

  ReportName = PdfLink.split("/")[-1]

  OutFileName = PdfLink.split("/")[-1].split(".")[0]
  MakeStix(IndicatorsSTIX, RelationshipSTIX, AttackPatternSTIX,CleanText , OutputDirectory + OutFileName)









InputDirectory = "/content/drive/MyDrive/FYP_APT_Reports_Input/"   # apt reports kept in input directory,             if you are locally keepinf files, leave blank
OutputDirectory = "/content/drive/MyDrive/FYP_APT_STIX_Output/"   # output STIX/JSON file in Output Directory         if you are locally keepinf files, leave blank
OutputDirectory = "/content/drive/MyDrive/FYP_Modified_Output/"
#os.chdir(InputDirectory)

#OutputDirectory = "/content/drive/MyDrive/FYP_APT_STIX_Output/"   # output STIX/JSON file in Output Directory         if you are locally keepinf files, leave blank
#os.chdir(OutputDirectory)
#print(len(os.listdir()))

#InputFiles = os.listdir()

#InputFiles



"""for i in InputFiles[25:]:

  MainFunction( InputDirectory + i, OutputDirectory)
  print(i)"""

#MainFunction( InputDirectory + InputFiles[104], OutputDirectory)

"""
MainFunction( "/content/Document1.pdf", OutputDirectory)
MainFunction( "/content/Document2.pdf", OutputDirectory)
MainFunction( "/content/Document3.pdf", OutputDirectory)
MainFunction( "/content/Document4.pdf", OutputDirectory)
MainFunction( "/content/Document5.pdf", OutputDirectory)
MainFunction( "/content/Document6.pdf", OutputDirectory)
MainFunction( "/content/Document7.pdf", OutputDirectory)
MainFunction( "/content/Document8.pdf", OutputDirectory)
MainFunction( "/content/Document9.pdf", OutputDirectory)
MainFunction( "/content/Document10.pdf", OutputDirectory)
"""

MainFunction( "/content/Aurora_Botnet_Command_Structure.pdf", "")