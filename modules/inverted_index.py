"""
    Defines Inerted Index class and helper functions
"""

from time import time
from math import sqrt, log
from gc import collect
from json import dumps, loads
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk import bigrams
from pandas import read_csv
from tqdm import tqdm
from utils import cosine_sim, string_vector, logger
from config import SHOW_PROGRESS_BAR, SCORE_THRESHOLD, REMOVE_STOP_WORDS, STOP_WORDS
from .TrieDS import Trie

def _minimum_edit_distance(s1, s2):
    """
        DP algorithm for minimum edit distance
    """
    if len(s1) == 0:
        return len(s2)
    if len(s2) == 0:
        return len(s1)
    m = len(s1)
    n = len(s2)
    dp = [[0 for j in range(n+1)] for i in range(m+1)]
    for i in range(m+1):
        for j in range(n+1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else:
                dp[i][j] = 1 + min(dp[i][j-1], dp[i-1][j], dp[i-1][j-1])
    return dp[m][n]

def _get_tf(pos, n):
    """
        Calculate tf
    """
    pos = sorted(pos)
    freq = {}
    for doc in pos:
        if doc in freq:
            freq[doc] += 1
        else:
            freq[doc] = 1
    for f in freq.keys():
        freq[f] = freq[f]/n[f]
    return freq


def _get_tf_idf(tf, df, N):
    """
        Calculate tf_idf
    """
    tf_idf = {}
    for f in tf.keys():
        tf_idf[f] = tf[f]*log(N/(df+1))
    return tf


class InvertedIndex(object):
    """
        Inverted Index using trie as data-structure
    """

    def __init__(self, paths):
        """
            Constructor to initialize trie, tokenizer and lemmatizer
        """
        self._trie = Trie()
        self._paths = sorted(paths)
        self._tokenizer = RegexpTokenizer(r'[^\W_]+')
        self._qtokenizer = RegexpTokenizer(r'[a-z0-9*?]+')
        self._stemmer = PorterStemmer()
        self._lemmatizer = WordNetLemmatizer()
        self._stop_words = STOP_WORDS

        # Warm up
        self._stemmer.stem(self._lemmatizer.lemmatize("united"))
        self._qtokenizer.tokenize("lol is lol")

        self._post2doc_mapper = {}
        self._n_docs = 0
        self._vocab = {}
        self._tf_idf_v = {}
        self._tmp_doc = {}
        self._bigrams = {}

    def initialize(self, paths=None):
        """
            Calculate Inverted Index and store in trie
        """
        if paths is None:
            paths = self._paths
        else:
            paths = sorted(paths)
            self._paths = paths
        
        itr = range(len(paths))
        if SHOW_PROGRESS_BAR:
            itr = tqdm(range(len(paths)), smoothing=0.7,
                           bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                           desc="Parsing CSV and creating posting list")

        for i_path in itr:
            self.from_csv(paths[i_path], i_path)

        itr = self._vocab
        if SHOW_PROGRESS_BAR:
            itr = tqdm(self._vocab,
                         bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                         desc="Creating Bigram Index")

        for word in itr:
            _bigrams = ["".join(i) for i in bigrams(word)]
            for bigram in _bigrams:
                if bigram in self._bigrams.keys():
                    self._bigrams[bigram].add(word)
                else:
                    self._bigrams[bigram] = {word}
        for bigram in self._bigrams:
            self._bigrams[bigram] = list(self._bigrams[bigram])

        itr = self._tmp_doc.keys()
        if SHOW_PROGRESS_BAR:
            itr = tqdm(self._tmp_doc.keys(), smoothing=0.7,
                        bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                        desc="Calculating tf_idf vector")

        for doc in itr:
            self._tf_idf_v[doc] = list(self.get_tfidf_vector(self._tmp_doc[doc]))+[len(self._tmp_doc[doc])]

        self._tmp_doc = None
        collect()

    def from_csv(self, path, doc_id):
        """
            read CSV and created inverted index for 'Snippet' column
        """
        try:
            csv = read_csv(path)
        except Exception as e:
            logger(str(e) + str(path))
            return

        # for i_row in tqdm(range(len(csv['Snippet'])),
        #                   bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
        #                   desc=("parsing csv file : " + path.split("/")[-1])):
        for i_row in range(len(csv['Snippet'])):
            tokens = self._tokenizer.tokenize(csv['Snippet'][i_row])
            if REMOVE_STOP_WORDS:
                tokens = [i for i in tokens if i not in self._stop_words]
            doc = self._n_docs+i_row
            self._post2doc_mapper[doc] = [doc_id, i_row]
            self._tmp_doc[doc] = []
            for token in tokens:
                if token in self._vocab.keys():
                    self._vocab[token] += 1
                else:
                    self._vocab[token] = 1
                term = self._stemmer.stem(self._lemmatizer.lemmatize(token))
                self._tmp_doc[doc].append(term)
                self._trie.add_string(term, doc)

        self._n_docs += len(csv['Snippet'])

    def search(self, string, mapped=True, lemstem=True):
        """
            Search string in trie
            map the hashed row-doc_id number returned from trie search as {doc_id: [rows]}
            return resultant {doc_id: [rows]}

        """
        if '*' not in string and lemstem:
            string = self._stemmer.stem(self._lemmatizer.lemmatize(string))
        poss = self._trie.search(string)
        if mapped:
            res = {}
            for pos in poss:
                doc_row = self._post2doc_mapper[pos]

                if doc_row[0] in res.keys():
                    res[doc_row[0]].add(doc_row[1])
                    break
                else:
                    res[doc_row[0]] = doc_row[1]
                    break
            return res, poss
        return poss

    def get_tfidf_vector(self, tokens: list, token_df={}):
        """
            Calculate tf_idf vector for given token wtr dataset
        """
        vector = {}
        norm = 0
        tmp_trie = None

        for string in set(tokens):
            _df = 0
            if string in self._vocab.keys():
                _df = self._vocab[string]
            elif string in token_df.keys():
                _df = token_df[string][1]
            _idf = (len(self._vocab)+1)/(_df+1)
            _tf = 0

            if '*' in string:
                if tmp_trie is None:
                    tmp_trie = Trie()
                    for token in tokens:
                        tmp_trie.add_string(token, 0)

                poss = tmp_trie.search(string)
                _tf = _get_tf(poss, [len(tokens)])[0]
            else:
                _tf = tokens.count(string)/len(tokens)

            tf_idf = _tf*_idf
            try:
                vector[string] = tf_idf
                norm += (tf_idf**2)
            except Exception as e:
                logger(e)

        norm = sqrt(norm)

        return vector, norm

    def _posible_token_match(self, token):
        """
            Spelling correction algorithm
        """
        _bigrams = ["".join(i) for i in bigrams(token)]
        possible_words = {}
        for bigram in _bigrams:
            if bigram in self._bigrams.keys():
                for word in self._bigrams[bigram]:
                    if word in possible_words.keys():
                        possible_words[word] += word.count(bigram)
                    else:
                        possible_words[word] = word.count(bigram)
        res = []
        for word in possible_words:
            if possible_words[word] > len(word)/2:
                sv_1 = string_vector(word)
                sv_2 = string_vector(token)
                min_edit = _minimum_edit_distance(word, token)
                if min_edit == 0:
                    min_edit = 0.01
                res.append((word, cosine_sim(sv_1, sv_2)/min_edit))
        res = sorted(res, key=lambda x: x[1], reverse=True)
        if res:
            return res[0][0]
        return None
        
    def _run_query_cos(self, query, top_n=-1, show_detail=True):
        """
            Match score(altered) algorithm for ranking query search
        """
        tokens = self._qtokenizer.tokenize(query)
        if REMOVE_STOP_WORDS:
            tokens = [i for i in tokens if i not in self._stop_words]
        tokens = [self._stemmer.stem(self._lemmatizer.lemmatize(i))
                  for i in tokens if len(i) > 0]
        poss = set()
        token_df = {}
        time_taken = {}

        itr = enumerate(tokens)
        if SHOW_PROGRESS_BAR:
            itr = tqdm(enumerate(tokens), total=len(tokens), bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                          desc="Searching for tokens from query in the Tire ")
        _now = time()
        for i_token, token in itr:
            new_poss = self.search(token, mapped=False, lemstem=False)
            if not new_poss and not ("*" in token or "?" in token):
                _possible_token = self._posible_token_match(token)
                logger("No possible matching found in docs for word: " + token)
                replace_token = ""

                if _possible_token:
                    replace_token = _possible_token
                    logger("Triyng " + _possible_token + " instead of " + token)
                    new_poss = self.search(_possible_token, mapped=False, lemstem=False)
                j_token = i_token + 1
                
                while j_token < len(tokens):
                    if tokens[j_token] == token:
                        tokens[j_token] = replace_token
                    j_token+=1
                tokens[i_token] = replace_token
            tmp_poss = set(new_poss)
            if "*" in token or "?" in token:
                token_df[token] = [{i:new_poss.count(i) for i in tmp_poss}, len(new_poss)]
            
            poss.update(tmp_poss)
        time_taken["Search"] = time() - _now
        if poss:
            res = {}
            itr = poss
            if SHOW_PROGRESS_BAR:
                itr = tqdm(poss, smoothing=0.7, bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                            desc="Mapping hashed doc to doc_is:[rows] ")
            
            _now = time()
            for pos in itr:
                doc_row = self._post2doc_mapper[pos]

                if doc_row[0] in res.keys():
                    res[doc_row[0]].append([doc_row[1], pos])
                else:
                    res[doc_row[0]] = [[doc_row[1], pos]]
            
            time_taken["Mapping back to original file"] = time() - _now
            results = []
            qtf_idf_vector, qnorm = self.get_tfidf_vector(tokens, token_df=token_df)

            itr = res.keys()
            if SHOW_PROGRESS_BAR:
                itr = tqdm(res.keys(), smoothing=0.7,
                              bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                              desc="Getting required row from csv files and "
                                    "calculating cos score")

            _now = time()
            for i_doc in itr:
                if show_detail:
                    csv = read_csv(self._paths[int(i_doc)])
                
                for i_row, doc in res[i_doc]:
                    r = {}
                    r['Path'] = self._paths[int(i_doc)]
                    r['Row_no'] = i_row

                    n_counter = 0

                    if show_detail:
                        for col in csv.columns:
                            r[col] = csv[col][i_row]
                    dtf_idf_vector, dnorm, n_tokens = self._tf_idf_v[doc]
                    dotp_sum = 0

                    for j in qtf_idf_vector:
                        if j in dtf_idf_vector.keys():
                            dotp_sum += dtf_idf_vector[j]*qtf_idf_vector[j]
                            n_counter += 1
                        elif  "*" in j or "?" in j:
                            if doc in token_df[j][0].keys():
                                tf_idf = (token_df[j][0][doc]/n_tokens)*((len(self._vocab)+1)/(token_df[j][1]+1))
                                dotp_sum += qtf_idf_vector[j]*tf_idf
                                dnorm = sqrt(dnorm**2 + tf_idf**2)
                                n_counter += 1
                    
                    cos_sin = 0
                    if qnorm != 0:
                        cos_sin = dotp_sum/(qnorm*dnorm)
                    r['rank_points'] = cos_sin*(n_counter/len(qtf_idf_vector))
                    if r['rank_points'] > SCORE_THRESHOLD:
                        results.append(r)

            time_taken["Fetching and calculating scores"] = time() - _now
            results = sorted(results, key=lambda x: x['rank_points'], reverse=True)
            results.append({})

            return results[:top_n], time_taken

        return [], time_taken

    def _run_query_match(self, query, top_n=-1, show_detail=True):
        """
            Cosine similarity algorithm for ranking query search
        """
        tokens = self._qtokenizer.tokenize(query)
        if REMOVE_STOP_WORDS:
            tokens = [i for i in tokens if i not in self._stop_words]
        tokens = [self._stemmer.stem(self._lemmatizer.lemmatize(i))
                  for i in tokens if len(i) > 0]

        

        poss = set()
        token_df = {}
        time_taken = {}
        itr = enumerate(tokens)
        if SHOW_PROGRESS_BAR:
            itr = tqdm(enumerate(tokens), total=len(tokens), bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                          desc="Searching for tokens from query in the Tire ")
        
        _now = time()
        for i_token, token in itr:
            new_poss = self.search(token, mapped=False, lemstem=False)
            if not new_poss and not ("*" in token or "?" in token):
                _possible_token = self._posible_token_match(token)
                logger("No possible matching found in docs for word: " + token)
                replace_token = ""

                if _possible_token:
                    replace_token = _possible_token
                    logger("Triyng " + _possible_token + " instead of " + token)
                    new_poss = self.search(_possible_token, mapped=False, lemstem=False)
                j_token = i_token + 1
                
                while j_token < len(tokens):
                    if tokens[j_token] == token:
                        tokens[j_token] = replace_token
                    j_token+=1
                tokens[i_token] = replace_token
            tmp_poss = set(new_poss)
            if "*" in token or "?" in token:
                token_df[token] = [{i:new_poss.count(i) for i in tmp_poss}, len(new_poss)]
            
            poss.update(tmp_poss)
        time_taken["Search"] = time() - _now
        if poss:
            res = {}
            itr = poss
            if SHOW_PROGRESS_BAR:
                itr = tqdm(poss, smoothing=0.7, bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                            desc="Mapping hashed doc to doc_is:[rows] ")
            _now = time()
            for pos in itr:
                doc_row = self._post2doc_mapper[pos]

                if doc_row[0] in res.keys():
                    res[doc_row[0]].append([doc_row[1], pos])
                else:
                    res[doc_row[0]] = [[doc_row[1], pos]]

            time_taken["Mapping back to original file"] = time() - _now
            results = []
            qtf_idf_vector, _ = self.get_tfidf_vector(tokens, token_df=token_df)

            itr = res.keys()
            if SHOW_PROGRESS_BAR:
                itr = tqdm(res.keys(), smoothing=0.7,
                              bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                              desc="Getting required row from csv files and "
                                    "calculating match score")

            _now = time()
            for i_doc in itr:
                if show_detail:
                    csv = read_csv(self._paths[int(i_doc)])

                for i_row, doc in res[i_doc]:
                    r = {}
                    r['Path'] = self._paths[int(i_doc)]
                    r['Row_no'] = i_row
                    
                    if show_detail:
                        for col in csv.columns:
                            r[col] = csv[col][i_row]

                    dtf_idf_vector, _, n_tokens = self._tf_idf_v[doc]
                    match_isum = 0
                    n_counter = 0
                    for j in qtf_idf_vector:
                        if j in dtf_idf_vector.keys():
                            match_isum += (dtf_idf_vector[j])
                            n_counter += 1
                        elif "*" in j or "?" in j:
                            if doc in token_df[j][0].keys():
                                tf_idf = (token_df[j][0][doc]/n_tokens)*((len(self._vocab)+1)/(token_df[j][1]+1))
                                match_isum += tf_idf
                                n_counter += 1
                    
                    r['rank_points'] = match_isum#*n_counter/100000
                    if r['rank_points'] > SCORE_THRESHOLD:
                        results.append(r)

            time_taken["Fetching and calculating scores"] = time() - _now
            results = sorted(results, key=lambda x: x['rank_points'], reverse=True)
            results.append({})

            return results[:top_n], time_taken

        return [], time_taken

    def run_query(self, query, ranking=False, top_n=-1, ranking_algo=None, show_detail=True):
        """
            Calls algo based query search anf ranking if specified or
            returns normal query search
        """
        if ranking:
            if ranking_algo == 'cos':
                return self._run_query_cos(query, top_n=top_n, show_detail=show_detail)
            elif ranking_algo == 'match':
                return self._run_query_match(query, top_n=top_n, show_detail=show_detail)

        tokens = self._qtokenizer.tokenize(query)
        if REMOVE_STOP_WORDS:
            tokens = [i for i in tokens if i not in self._stop_words]
        tokens = [self._stemmer.stem(self._lemmatizer.lemmatize(i))
                  for i in tokens if len(i) > 0]

        poss = set()
        time_taken = {}
        itr = enumerate(set(tokens))
        if SHOW_PROGRESS_BAR:
            itr = tqdm(enumerate(set(tokens)), total=len(tokens), bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                          desc="Searching for tokens from query in the Tire ")
        _now = time()
        for i_token, token in itr:
            new_poss = self.search(token, mapped=False, lemstem=False)
            if not new_poss:
                _possible_token = self._posible_token_match(token)
                logger("No possible matching found in docs for word: " + token)
                replace_token = ""

                if _possible_token:
                    replace_token = _possible_token
                    logger("Triyng " + _possible_token + " instead of " + token)
                    new_poss = self.search(_possible_token, mapped=False, lemstem=False)
                j_token = i_token + 1

                while j_token < len(tokens):
                    if tokens[j_token] == token:
                        tokens[j_token] = replace_token
                tokens[i_token] = replace_token

            poss.update(new_poss)
        time_taken["Search"] = time() - _now
        if poss:
            res = {}
            itr = poss
            if SHOW_PROGRESS_BAR:
                itr = tqdm(poss, smoothing=0.7, bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                            desc="Mapping hashed doc to doc_is:[rows] ")
            _now = time()
            for pos in itr:
                doc_row = self._post2doc_mapper[pos]

                if doc_row[0] in res.keys():
                    res[doc_row[0]].append([doc_row[1], pos])
                else:
                    res[doc_row[0]] = [[doc_row[1], pos]]
            time_taken["Mapping back to original file"] = time() - _now
            results = []

            itr = res.keys()
            if SHOW_PROGRESS_BAR:
                itr = tqdm(res.keys(), smoothing=0.7,
                              bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                              desc="Getting required row from csv files and "
                                    "calculating match score")
            _now = time()
            for i_doc in itr:
                if show_detail:
                    csv = read_csv(self._paths[int(i_doc)])
                for i_row in res[i_doc]:
                    r = {}
                    r['Path'] = self._paths[int(i_doc)]
                    r['Row_no'] = i_row
                    if show_detail:
                        for col in csv.columns:
                            r[col] = csv[col][i_row]
                    results.append(r)
            time_taken["Fetching data from file"] = time() - _now
            return results[:top_n], time_taken

        return [], time_taken

    def save(self, filepath):
        """
            Save Inverted Index - Posting List as posting_list.json
            and hashed row-doc_id as pos2doc.json
        """
        bar = tqdm(total=5, smoothing=0.7, bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                   desc="Saving emgine model ")
        file_writer = open(filepath+"posting_list.json", 'w')
        file_writer.write(dumps(self._trie.to_dict()))
        file_writer.close()
        bar.update(1)
        file_writer = open(filepath+"pos2doc.json", 'w')
        file_writer.write(dumps(self._post2doc_mapper))
        file_writer.close()
        bar.update(1)
        file_writer = open(filepath+"tf_idf_vector.json", 'w')
        file_writer.write(dumps(self._tf_idf_v))
        file_writer.close()
        bar.update(1)
        file_writer = open(filepath+"bigrams.json", 'w')
        file_writer.write(dumps(self._bigrams))
        file_writer.close()
        bar.update(1)
        file_writer = open(filepath+"vocab.json", 'w')
        file_writer.write(dumps(self._vocab))
        file_writer.close()
        bar.update(1)

    def load(self, filepath):
        """
            Load data from saved posting list and hashed row-doc_id mapper
        """
        bar = tqdm(total=5, smoothing=0.7, bar_format='{l_bar}{bar:50}{r_bar}{bar:-50b}',
                   desc="Loading engine model ")
        file_reader = open(filepath+"posting_list.json", 'r')
        self._trie.from_dict(loads(file_reader.read()))
        file_reader.close()
        bar.update(1)
        file_reader = open(filepath+"bigrams.json", 'r')
        self._bigrams = loads(file_reader.read())
        file_reader.close()
        bar.update(1)
        file_reader = open(filepath+"pos2doc.json", 'r')
        mapper = loads(file_reader.read())
        file_reader.close()
        self._post2doc_mapper = {int(i): [mapper[i][0], int(mapper[i][1])] for i in mapper.keys()}
        bar.update(1)
        file_reader = open(filepath+"tf_idf_vector.json", 'r')
        tf_idf = loads(file_reader.read())
        self._tf_idf_v = {int(i): [{j: float(tf_idf[i][0][j])
                                    for j in tf_idf[i][0].keys()}, float(tf_idf[i][1]), int(tf_idf[i][2])] for i in tf_idf.keys()}
        file_reader.close()
        bar.update(1)
        file_reader = open(filepath+"vocab.json", 'r')
        self._vocab = loads(file_reader.read())
        for k in self._vocab.keys():
            self._vocab[k] = int(self._vocab[k])
        file_reader.close()
        bar.update(1)
