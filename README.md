## Trie based inverted index


### Install Requirements and Elastic Search

```bash
pip3 install -r requirements.txt
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.10.0
```


### Download required nltk data and load the elastic engine

**Open two terminals**

 - ```bash
   docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.10.0
    ```
 - ```bash
   python3 initialize.py
   ```

### To do search on Trie Search Engine

```bash
python3 main.py
```

### To compare Elastic ansd Trie Search Engine

**Make sure SHOW_DETAIL is set to True in config file before running this**

```bash
python3 search.py
```

### To benchmark the Trie Search Engine

**Make sure SHOW_DETAIL is set to True in config file before running this**

```bash
python3 benchmark.py
```


### How to change configuration

Go to config.py in config directory.

#### Changeable configs:
 - DATA_PATH = Path to csv files
 - ENGINE_PATH = Path were data required by engine is stored
 - LOG_FILE = Path where log file is stored
 - RANKING = Boolean (True or False), specifies if you want to rank the output or not
 - SHOW_DETAIL = Boolean (True or False), specifies if you want to extract data from csv and show along with the result
 - RANKING_ALGO = Specifies type of ranking algorithm you want to adopt. Options = "cos", "match"
 - TOTAL_N_RESULT = Number of top results to be displayed
 - SHOW_PROGRESS_BAR = Boolean (True or False), To show the progress bar
 - SCORE_THRESHOLD = default:1e-4, score below this will not be displayed or returned
 - REMOVE_STOP_WORDS = Boolean (True or False), If you want to remove specified stopwords
 - STOP_WORDS = set of tokens which won't we considered for indexing or for running query if REMOVE_STOP_WORDS is true

