"""
    Comparing Elastic and Trie
"""

from os import listdir
from modules import InvertedIndex
from config import DATA_PATH, REQUIRED_FILE_FOR_ENGINE, ENGINE_PATH
from config import RANKING_ALGO, SHOW_DETAIL, TOTAL_N_RESULT, RANKING
from utils import logger, elastic_search, trie_search
import sys
import time
import json
from elasticsearch import helpers, Elasticsearch
import csv


_IS_ENGINE = True

if __name__ == "__main__":
    """
        Main function that run search engine
    """
    # Check if engine is already saved else create and save
    paths = sorted([DATA_PATH+i for i in listdir(DATA_PATH)])
    engine = InvertedIndex(paths)
    es = Elasticsearch([{'Host':'localhost','port':9200}])
    for file_i in REQUIRED_FILE_FOR_ENGINE:
        if file_i not in listdir(ENGINE_PATH):
            _IS_ENGINE = False
            engine.initialize()
            engine.save(ENGINE_PATH)
            break

    if _IS_ENGINE:
        engine.load("engine/")
    while 1:
        try:
            query = input("[Note: Press Ctrl+C to abort]\nEnter Search Query : ")
        except Exception as exe:
            logger(exe)
            exit(0)
        
        query = query.lower()
        # Elastic Search
        es_res, es_time_taken = elastic_search(es, query)

        # Trie Search
        trie_res, t_time_taken = trie_search(engine, query)

        print("Time Taken by Elastic Search = ", es_time_taken)
        print("Time Taken by Trie Search = ", t_time_taken)
        print("\n\nElastic search top 10 : ")
        for i,j in enumerate(es_res[:10]):
            print(i, ".", j)
        print("\n\nTrie search top 10 : ")
        for i,j in enumerate(trie_res[:10]):
            print(i, ".", j)
        totalSize = 94857

        actual = trie_res
        expected = es_res
        
        # Metrics Calculation
        metrics = {}
        try:
            metrics['tp'] = len(list(set(actual) & set(expected)))
            metrics['fp'] = len(list(set(actual).difference(set(expected))))
            metrics['tn'] = totalSize - len(list(set(actual).union(set(expected))))
            metrics['fn'] = len(list(set(expected).difference(set(actual))))
            metrics['acc'] = metrics['tp'] + metrics['tn']
            metrics['acc'] = metrics['acc']/(metrics['tp'] + metrics['tn'] + metrics['fp'] + metrics['fn'])
            metrics['rec'] = metrics['tp']/(metrics['tp'] + metrics['fn'])
            try:
                metrics['prec'] = metrics['tp']/(metrics['tp'] + metrics['fp'])
            except:
                metrics['prec'] = 0
            try:
                metrics['f1'] = metrics['prec'] *metrics['rec']*2 / (metrics['prec'] + metrics['rec'])
            except:
                metrics['f1'] = 0
        except:
            pass
        
        print("\n\nScore : \n", metrics)

        _y_n = input("Want to continue?[y/N]")
        if not _y_n:
            break
        if _y_n.lower() == "n":
            break
        if _y_n.lower() == "y":
            sys.stderr.write("\x1b[2J\x1b[H")
            continue
        print("wrong input")
        sys.exit(1)
        

