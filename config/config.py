"""
    Loads config file
"""
# from json import loads
from nltk.corpus import stopwords


# f_config = open("./config.json", "r")

# SEARCH_ENGINE_CONFIG = loads(f_config.read())

# f_config.close()

######################################### DON'T CHANGE THIS ########################################################
REQUIRED_FILE_FOR_ENGINE = ["posting_list.json", "pos2doc.json", "vocab.json", "tf_idf_vector.json", "bigrams.json"]
####################################################################################################################


########################################### CHANGEABLE ##############################################################
DATA_PATH = "./data/"

ENGINE_PATH = "./engine/"

LOG_FILE = "./log/log.logs"

RANKING = True

SHOW_DETAIL = True

RANKING_ALGO = 'match'

TOTAL_N_RESULT = 3000

SHOW_PROGRESS_BAR = False

SCORE_THRESHOLD = 1e-4

REMOVE_STOP_WORDS = False

STOP_WORDS = set(['i', 'a', 'an', 'are', 'as', 'at', 'be', 'by', 'in', 'is',
                  'it', 'of', 'on', 'or', 'the', 'to', 'was'])

# STOP_WORDS = set(stopwords.words('english'))
####################################################################################################################
