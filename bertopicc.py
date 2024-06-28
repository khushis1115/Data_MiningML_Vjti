from bertopic import BERTopic
import json
import pandas as pd
with open("data/vol17.json", 'r', encodings="utf-8") as f:
    docs=json.load(f)["descriptions"]
len(docs)
