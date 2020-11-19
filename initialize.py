"""
    Initialize nltk and elastic search
"""
import nltk
import csv
import os
from elasticsearch import helpers, Elasticsearch
from config import DATA_PATH
from utils import csv_to_json


# Dowload the wordnet corpus for nltk
nltk.download('punkt')
nltk.download('wordnet')





path = DATA_PATH
paths = sorted([path+i for i in os.listdir(path)])
es = Elasticsearch([{'Host':'localhost','port':9200}])

i = 0
for file_i in paths:
    with open(file_i) as f:
        reader = csv.DictReader(f)
        helpers.bulk(es, reader, index='my-index', doc_type='my-type')
    i += 1
