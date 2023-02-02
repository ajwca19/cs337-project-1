# Importing necessary modules
import pandas as pd
import nltk
from nltk.cluster import KMeansClusterer
import re
import random
from heapq import nlargest
from gensim.models import Word2Vec
import numpy as np

# Writing helper functions
# Function to import the gg2013 tweets file
#def import_tweets():
#    global tweets
#    tweets = pd.read_json('gg2013.json')
#    for i in range(0, len(tweets)): 
#        cleaned_tweet = clean_tweet(tweets.loc[i]['text'])
#        tweets.at[i, 'text'] = cleaned_tweet
#    return

# Function to process the gg2013 tweets file
#def clean_tweet(tweet_text):
#    retweet_re = "^[rR][tT] @[a-zA-Z0-9_]*: "
#    hyperlink_re = "http://[a-zA-Z0-9./-]*"
#    hashtag_re = "#[a-zA-Z0-9_]+"
#    return re.sub(hyperlink_re, "", tweet_text)

# Function to search tweets for the specified regular expression, and save the top N hashtags
def search_tweets(tweets, reg_ex, ht_num):
    returned_tweets = [] # List of tweets matching specified regular expression
    hashtags = {} # Dictionary of hashtags used in tweets
    for j in range(0, len(tweets)):
        text = tweets.loc[j]['text'].lower()
        if re.search(reg_ex, text) and not re.search("^[Rr][Tt]", text): # No retweets
            returned_tweets.append(text) # Save a tweet if it contains the specified regular expression
            matches = re.finditer("#[a-z0-9]+\s{1}|#[a-z0-9]+$", text) # Among the extracted tweets, pull out and save all the unique hashtags
            for hashtag in matches:
                ht = re.sub("#", "", hashtag.group().strip())
                if ht not in hashtags:
                    hashtags[ht] = 1
                else:
                    hashtags[ht] += 1
    # Keeping the top N hashtags
    hashtags_list = nlargest(ht_num, hashtags, key = hashtags.get)
    return (returned_tweets, hashtags_list)

# Function to extract all possible words of length min_len-max_len from the saved hashtags
def hashtag_extract(hashtags_list, min_len, max_len):
    word_count = 0
    position_count = 0
    word_length = min_len
    extracted_word_list = []
    while word_count < len(hashtags_list):
        while word_length <= max_len:
            while position_count <= len(hashtags_list[word_count]) - word_length:
                extracted_word = ""
                for i in range(0, word_length):
                    extracted_word += hashtags_list[word_count][position_count + i]
                extracted_word_list.append(extracted_word)
                position_count += 1
            word_length += 1
            position_count = 0
        word_count += 1
        position_count = 0
        word_length = min_len
    return extracted_word_list

# Function to extract and clean possible award names from the returned tweets, and generate word embeddings for the possible award names
def award_extract(tweets, extracted_word_list):
    # Splitting the possible tweets mentioning awards on best, and keeping only the right-hand side
    possible_award_names = []
    for award in tweets:
        split_award = award.split("best")
        split_award_rhs = split_award[1]
        split_award_rhs = "best" + split_award_rhs # Appending 'best' back to the beginning of the right-hand side
        # Cleaning up the possible award names by taking some extra stuff out
        split_award_rhs = re.sub(" for .*", "", split_award_rhs) # Deleting everything that falls after the word "for", which is usually the winner name
        split_award_rhs = re.sub("#.*", "", split_award_rhs) # Deleting everything that falls after a hashtag, since these are usually after the award names
        split_award_rhs = re.sub("@.*", "", split_award_rhs) # Deleting everything that falls after an @
        split_award_rhs = re.sub("\.|!.*", "", split_award_rhs) # Deleting everything that falls after a period or exclamation point, since these are after award names
        split_award_rhs = re.sub(" at .*", "", split_award_rhs) # Deleting everything that falls after "at ", since that is usually followed by the ceremony name
        split_award_rhs = re.sub("http.*", "", split_award_rhs) # Deleting all web addresses
        split_award_rhs = re.sub("congrat.*", "", split_award_rhs) # Deleting everything following "congrats" or "congratulations"
        for word in reversed(extracted_word_list): # Deleting all possible words from the top N unique hashtags
            split_award_rhs = re.sub(word, "", split_award_rhs)    
        split_award_rhs = re.sub(",", "-", split_award_rhs) # Changing all commas to dashes
        split_award_rhs = re.sub("-$", "", split_award_rhs) # Deleting all dashes that end lines
        split_award_rhs = re.sub("\\n", "", split_award_rhs) # Deleting all new line symbols
        split_award_rhs = re.sub(r'([a-z])(-)', r'\g<1> \g<2>', split_award_rhs) # Adding a space in between a character and dash
        split_award_rhs = re.sub(r'(-)([a-z])', r'\g<1> \g<2>', split_award_rhs) # Adding a space in between a dash and character
        split_award_rhs = re.sub(" +", " ", split_award_rhs) # Changing all multiple spaces to single spaces
        split_award_rhs = split_award_rhs.strip() # Deleting leading and trailing spaces
        split_award_rhs_list = split_award_rhs.split(" ") # Splitting the possible awards names into separate words, generating a list of lists
        possible_award_names.append(split_award_rhs_list)
    # Generating word embeddings for each word contained in the possible award names using Word2Vec
    embeddings = Word2Vec(possible_award_names, min_count = 1)
    return (possible_award_names, embeddings)

# Function to average the word embeddings for each word comprising each unique possible award name
def create_award_embedding(possible_award, embeddings):
    award_embedding = []
    award_word_number = 0
    for word in possible_award:
        if award_word_number == 0:
            award_embedding = embeddings.wv[word]
        else:
            award_embedding = np.add(award_embedding, embeddings.wv[word])
        award_word_number += 1
    return np.asarray(award_embedding) / award_word_number

# Function to generate the award-level embeddings for each unique possible award name, and cluster the award-level embeddings using K-means clustering
def cluster_award_embeddings(possible_award_names, embeddings, cluster_num):
    # Generating the award-level embeddings for each unique possible award name
    award_embeddings = []
    for possible_award in possible_award_names:
        award_embeddings.append(create_award_embedding(possible_award, embeddings))
    # Clustering the award-level embeddings into N clusters using K-means clustering
    rng = random.Random()
    rng.seed(321)
    kmeans = KMeansClusterer(cluster_num, distance = nltk.cluster.util.cosine_distance, repeats = 10, avoid_empty_clusters = True, rng = rng)
    award_clusters = kmeans.cluster(award_embeddings, assign_clusters = True)
    # Joining together the individual words of the possible award names to generate one phrase per award
    possible_award_names_clusters = []
    for award in possible_award_names:
        full_award_name = ' '.join(award)
        possible_award_names_clusters.append(full_award_name)
    # Linking in the assigned award clusters to each award name
    award_clusters_dict = {}
    for i in range(len(award_clusters)):
        if award_clusters[i] not in award_clusters_dict:
            award_clusters_dict[award_clusters[i]] = []
        if possible_award_names_clusters[i] not in award_clusters_dict[award_clusters[i]]:
            award_clusters_dict[award_clusters[i]].append(possible_award_names_clusters[i])
    return (possible_award_names_clusters, award_clusters_dict)

# Function to select the most frequently mentioned possible award name from each cluster, if the possible award name was tweeted at least min_tweet times
# *Returns final list of inferred award names*
def final_awards(possible_award_names_clusters, award_clusters_dict, min_tweet):
    # Counting the occurrences of all possible award names
    possible_award_names_count = {}
    for award in possible_award_names_clusters:
        if award != "best": # Possible award string is not only the word "best"
            if award not in possible_award_names_count:
                possible_award_names_count[award] = 1
            else:
                possible_award_names_count[award] += 1
    # Selecting the most frequently mentioned possible award name from each cluster, if the possible award name was tweeted at least min_tweet times
    final_awards = []
    for cluster, award_names in award_clusters_dict.items():
        max_tweet_frequency = min_tweet
        final_award = ""
        for award in award_names:
            for aw, count in possible_award_names_count.items():
                if award == aw and count > max_tweet_frequency:
                    max_tweet_frequency = count
                    final_award = award
                elif award == aw and count > min_tweet and count == max_tweet_frequency:
                    if random.randint(0, 1) == 1:
                        final_award = award
        final_awards.append(final_award)
    # Removing empty strings from the list of final award names
    while "" in final_awards:
        final_awards.remove("")
    return final_awards