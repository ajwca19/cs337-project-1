# Importing necessary modules
import pandas as pd
import nltk
from nltk.cluster import KMeansClusterer
import re
import random
from heapq import nlargest
from gensim.models import Word2Vec
import numpy as np

# Function to import and process the gg2013 tweets file
def import_tweets(json_file):
    tweets = pd.read_json(json_file)
    # Subsetting to tweets that are not retweets
    no_retweets = []
    for j in range(0, len(tweets)):
        text = tweets.loc[j]['text']
        if not re.search("^RT", text):
            no_retweets.append(text.lower())
    no_retweets_df = pd.DataFrame({'text': no_retweets})
    return no_retweets_df

# Importing the gg2013 tweets file
no_retweets_df = import_tweets('gg2013.json')

print(no_retweets_df)