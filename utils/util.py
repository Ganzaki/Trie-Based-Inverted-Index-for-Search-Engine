import os
from numpy import dot, linalg, array, zeros
from config import RANKING_ALGO, SHOW_DETAIL, TOTAL_N_RESULT, RANKING
from time import time
import csv

def string_vector(string):
    """
        Create vector for given string using alphabet as i-th index
    """
    s_v = zeros(26)
    for i,j in enumerate(string):
        try:
            s_v[ord(j)-ord('a')] += 1
        except Exception as exe:
            pass
    return s_v


def cosine_sim(a, b):
    """
        Calculate cosine similarity for a and b
    """
    cos_sim = dot(a, b)/(linalg.norm(a)*linalg.norm(b))
    return cos_sim

def csv_to_list(path):
    """
    """
    f = open(path, "r")
    lines = f.readlines()
    req_list = [line.split(",") for line in lines]
    return req_list


def csvs_from_directory(path):
    """
        Dictionary of csv data where key is csv file name
    """
    assert(os.path.isdir(path))
    csvs = os.listdir(path)
    if path[-1] != '/':
        path += '/'
    
    doc_token = {}
    for csv in csvs:
        doc_token[csv] = csv_to_list(csv)
    
    return doc_token


def csv_to_json(csvFile):
    """
        Convert csv to json format
    """
    data = dict()
    with open(csvFile, encoding='utf-8') as csvf: 
        csvReader = csv.DictReader(csvf)
        for rows in csvReader: 
            key = rows['\ufeffURL'] 
            data[key] = rows 
    return data


def elastic_search(es, query):
    """
        Run query on elastic search and return result, time_taken
    """
    ans = []
    now = time()
    a = es.search(index="my-index", body={'query':{"match": {"Snippet":query}}}, size=TOTAL_N_RESULT)
    for i in a['hits']['hits']:
        if i['_source']['Snippet'] not in ans and i['_score'] > 0.1:
            ans.append(i['_source']['Snippet'])
    time_taken = time() - now
    return ans, time_taken


def trie_search(engine, query):
    """
        Run query on trie search and return result, time_taken
    """
    res, time_taken = engine.run_query(query,
                                       ranking=RANKING,
                                       ranking_algo=RANKING_ALGO,
                                       top_n=TOTAL_N_RESULT,
                                       show_detail=SHOW_DETAIL)
    ans = []
    for i in res:
        if 'Snippet' in i.keys():
            ans.append(i['Snippet'])
    return ans, time_taken