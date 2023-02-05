'''Version 0.35'''

#importing necessary modules
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.cluster import KMeansClusterer
import re
import random
import spacy
import json
from spacy import displacy
from collections import Counter
#python -m spacy download en
import en_core_web_sm
from heapq import nlargest
from gensim.models import Word2Vec
import numpy as np
from textblob import TextBlob
from spacytextblob.spacytextblob import SpacyTextBlob

nlp = en_core_web_sm.load()
nltk.download("punkt", quiet = True)

#import external files used in solution
import host_names
import awards_from_ceremony
import winners_from_awards_and_nominees
import fashion

#-------------------- VARIABLES GIVEN IN GG_API FILE ------------------
OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

#----------- OUR VARIABLES ---------------
ceremony_name = "Golden Globes"

#list of buckets for corresponding functions/algorithms
host_bucket = []
award_bucket = []
presenter_bucket = []
nominees_bucket = []
winner_bucket = []
fashion_bucket = []


#--------------- HELPER FUNCTIONS BELOW ----------------------
# Function to clean imported tweets
def clean_tweet(tweet_text):
    retweet_re = "^[rR][tT] @[a-zA-Z0-9_]*: "
    hyperlink_re = "http://[a-zA-Z0-9./-]*"
    hashtag_re = "#[a-zA-Z0-9_]+"
    return re.sub(hyperlink_re, "", tweet_text)

# Function to identify the award based on the text of a tweet
def identify_award(award_list_split, tweet_text):
    award_similarities = [] # Metric trying to figure out how similar the text of a tweet is to each award
    curr_award_number = 0
    for award in award_list_split: # Loop through awards to get individual lists of keywords
        award_similarities.append(0) # Start the tally at 0
        for word in award: # Look for each of the keywords in the award
            if re.search(word, tweet_text):
                award_similarities[curr_award_number] += 1 # Add one to the tally because the tweet has the keyword
        curr_award_number += 1
    if sum(award_similarities) != 0: # At least one award was relevant to the text of a tweet
        # Reset award number count and figure out the index of the award with the max similarity
        curr_award_number = 0 # Reset curr_award_number
        likely_award_number = 0
        likely_award_max = -1
        for award_similarity in award_similarities:
            if award_similarity > likely_award_max:
                likely_award_max = award_similarity
                likely_award_number = curr_award_number
            elif award_similarity == likely_award_max: # Handle tie cases
                if random.randint(0, 1) == 1:
                    likely_award_number = curr_award_number
            curr_award_number += 1
        return likely_award_number
    else:
        return None

def add_to_buckets(tweet):
    tweet_text = tweets.loc[i]['text']
    #for hosts
    if re.search("host(s*)", tweet_text.lower()) and not re.search("^[Rr][Tt]", tweet_text):
        #conditions for being in host bucket
        host_bucket.append(re.sub(hashtag_re, "", tweet_text))
    
    #for fashion
    fashion_keywords = ["dress", "outfit", "fashion", "red carpet", "suit", "look", "jewelry", "accessor[y|ies]"]
    for keyword in fashion_keywords:
        if re.search(keyword, tweet_text.lower()) and not re.search("^[Rr][Tt]", tweet_text):
            fashion_bucket.append(re.sub(hashtag_re, "", tweet_text))
    
#----------- INCLUDED FUNCTIONS --------------
def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    hosts = host_names.get_names(host_bucket, ceremony_name + " " + str(year))
    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Searching tweets for awards and saving the top 10 hashtags
    possible_award_tweets, hashtags_list = awards_from_ceremony.search_tweets(tweets, "wins best|nominated for best", 10)
    # Extracting all possible words of length 4-20 from the saved hashtags
    extracted_word_list = awards_from_ceremony.hashtag_extract(hashtags_list, 4, 20)
    # Extracting and cleaning possible award names from the returned tweets, and generating word embeddings for the possible award names
    possible_award_names, embeddings = awards_from_ceremony.award_extract(possible_award_tweets, extracted_word_list)
    # Generating the award-level embeddings for each unique possible award name, and clustering the award-level embeddings into 25 clusters using K-means clustering
    possible_award_names_clusters, award_clusters_dict = awards_from_ceremony.cluster_award_embeddings(possible_award_names, embeddings, 25)
    # Selecting the most frequently mentioned possible award name from each cluster, if the possible award name was tweeted at least twice
    global awards
    awards = awards_from_ceremony.final_awards(possible_award_names_clusters, award_clusters_dict, 1)
    # Returns final list of inferred award names: awards
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    global nominees
    nominees = nominee_from_tweets.main(tweets, ceremony_name, year, OFFICIAL_AWARDS_1315)
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Processing the award names and creating intial data structures
    award_list_split_updated, award_list_unsplit, match_count_dict, sentiment_polarity_dict = winners_from_awards_and_nominees.awards_process(awards)
    # Going through each tweet and trying to find each award and nominee
    match_count_dict, sentiment_polarity_dict = winners_from_awards_and_nominees.winner_match(tweets, award_list_split_updated, nominees, award_list_unsplit, match_count_dict, sentiment_polarity_dict)
    # Find the nominee winner based on the "votes", and linking in the average tweet sentiment of them winning
    winners = winners_from_awards_and_nominees.identify_winner(match_count_dict, sentiment_polarity_dict)
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    # Your code here
    return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Reading in and processing the gg2013 tweets file:
    # Change file name below to change tweet database
    global tweets
    tweets = pd.read_json('gg2013.json')
    for i in range(0, len(tweets)): 
        cleaned_tweet = clean_tweet(tweets.loc[i]['text'])
        add_to_buckets(cleaned_tweet)
        tweets.at[i, 'text'] = cleaned_tweet
    print("Pre-ceremony processing complete.")
    return

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    # Your code here
    pre_ceremony()
    year = 2013
    print("Ceremony:", ceremony_name, year)
    
    #extracting hosts
    hosts = get_hosts(year)
    if len(hosts) == 1:
        print("The host is: " + hosts[0])
    else:
        host_name_string = hosts[0]
        for i in range(1, len(hosts) - 1):
            host_name_string = host_name_string + ", " + hosts[i]
        host_name_string = host_name_string + " & " + hosts[-1]
        print("The hosts are: " + host_name_string)
        
    #extracting awards
    awards = get_awards(year)
    award_name_string = awards[0].title()
    for i in range(1, len(awards) - 1):
        award_name_string = award_name_string + ", " + awards[i].title()
    award_name_string = award_name_string + ", & " + awards[-1].title()
    print("The award categories are:", award_name_string)
    
    #extracting nominees
    nominee_dict = get_nominees(year)
    # How to use nominee list -> nominee_from_tweets.nominee_all_list
    # ['paul rudd', 'daniel craig', 'damian lewis', 'kevin costner', ... ]
    # print(nominee_from_tweets.nominee_all_list)
    nominees_list = winners_from_awards_and_nominees.nominees_list() # *********** CHANGE THIS NOMINEES_LIST TO THE INFERRED NOMINEES ***************
    
    #extracting presenters
    
    #extracting winners
    winners = get_winner(year)
    print("The winners are:")
    for award, winner in winners.items():
        print(award.title() + ": " + winner['winner'].title() + ", with an average sentiment of " + str(winner['average_polarity']))
        
    #extracting best/worst dressed:
    best_dressed, worst_dressed = fashion.best_worst_dressed(fashion_bucket)
    best_dressed_string = best_dressed[0]
        for i in range(1, len(best_dressed) - 1):
            best_dressed_string = best_dressed_string + ", " + best_dressed[i]
        best_dressed_string = best_dressed_string + " & " + best_dressed[-1]
    worst_dressed_string = worst_dressed[0]
        for i in range(1, len(worst_dressed) - 1):
            worst_dressed_string = worst_dressed_string + ", " + worst_dressed[i]
        worst_dressed_string = worst_dressed_string + " & " + worst_dressed[-1]
    print("The best dressed of the night are: " + best_dressed_string)
    print("The worst dressed of the night are: " + worst_dressed_string)
    #putting official answers in the json file
    json_object = {}
    json_object["Hosts"] = hosts
    j
    return

if __name__ == '__main__':
    main()