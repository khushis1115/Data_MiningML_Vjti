import os
import tensorflow as tf
import warnings
from transformers import BertTokenizer, TFBertModel

# Initialize the BERT tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

# Sample text
text = "Hello, how are you?"

# Tokenization, Adding Special Tokens, Padding, and Truncation
inputs = tokenizer(
    text,
    return_tensors='tf',  # Return TensorFlow tensors
    max_length=10,  # Maximum length of the sequence
    padding='max_length',  # Pad to the maximum length
    truncation=True  # Truncate sequences longer than max_length
)

# Extract input_ids and attention_mask
input_ids = inputs['input_ids']
attention_mask = inputs['attention_mask']
token_type_ids= inputs['token_type_ids']
print(inputs.keys())
'''
print("Input IDs:", input_ids)
print("Attention Mask:", attention_mask)
print("Token_type_ids:", token_type_ids)
'''
# Initialize the BERT model
bert_model = TFBertModel.from_pretrained('bert-base-uncased')

# Pass inputs through BERT model
outputs = bert_model(input_ids, attention_mask=attention_mask)
print(outputs.keys())

'''
# The last hidden state
last_hidden_state = outputs.last_hidden_state
print("Last Hidden State:", last_hidden_state)
'''
pooler_output = outputs.pooler_output
print("Pooler Output:", pooler_output)
