# Importing necessary modules
import pandas as pd
import nltk
import re
import random
from textblob import TextBlob

import gg_api

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

# Function to process the nominee answers
def nominees_list():
    answers = pd.read_csv('answers.csv', usecols = ['nominees'])
    nominees_list = []
    for i in range(0, len(answers)):
        nominee = answers.loc[i]['nominees']
        nominee = nominee.replace('[', '')
        nominee = nominee.replace(']', '')
        nominee = nominee.split(',')
        nominee = [n.strip() for n in nominee]
        nominees_list.append(nominee)
    return nominees_list

# Function to process the award names and create initial data structures
def awards_process(awards_list):
    award_list_split = [] # List of list of keywords in each award split on spaces
    award_list_unsplit = [] # List of all of the award names in a single string
    for i in range(0, len(awards_list)):
        # Add award name and all words in the award to respective lists
        award_name = awards_list[i]
        award_list_unsplit.append(award_name)
        award_name_list = award_name.split(" ")
        award_list_split.append(award_name_list)
    stop_words = ["a", "an", "by", "or", "with", "in", "-", "best", "award", "for", "b."]
    award_list_split_updated = [] # Taking out stopwords from award_list_split, producing list of list of keywords
    for award in award_list_split:
        award_updated = []
        for word in award:
            if word not in stop_words:
                award_updated.append(word)
        award_list_split_updated.append(award_updated)
    # Dictionary mapping [award name (unsplit) -> [nominee -> mention count]]
    match_count_dict = {}
    # Dictionary mapping [award name (unsplit) -> [nominee -> tweet sentiment]]
    sentiment_polarity_dict = {}
    # Adding award names as keys to the dictionaries
    for award_name in award_list_unsplit:
        match_count_dict[award_name] = {}
        sentiment_polarity_dict[award_name] = {}
    return (award_list_split_updated, award_list_unsplit, match_count_dict, sentiment_polarity_dict)

# Function to go through each tweet that says 'wins' and try to identify which award and nominee it's associated with
def winner_match(tweets, award_list_split_updated, nominees_list, award_list_unsplit, match_count_dict, sentiment_polarity_dict):
    for j in range(0, len(tweets)):
        tweet_list = tweets[j].split("wins")
        if len(tweet_list) == 2: # Tweet has the word "wins"
            tweet_nominees = tweet_list[0] # Left side of the word wins, assumed to contain the name of nominees
            tweet_award = tweet_list[1] # Right side of the word wins, assumed to contain the name of awards
            likely_award_number = gg_api.identify_award(award_list_split_updated, tweet_award)
            if likely_award_number is not None:
                # Try to identify the nominee based on the nominees for the most likely award
                # Also perform sentiment analysis on the tweets to get a sense of people's opinions on a nominee winning their award
                for nominee in nominees_list[likely_award_number]:
                    if re.search(nominee, tweet_nominees):
                        # Nominee name shows up on left side of word "wins"
                        full_award_name = award_list_unsplit[likely_award_number]
                        sentiment = TextBlob(text) # Sentiment of the tweet mentioning the nominee 'wins'
                        polarity = sentiment.sentences[0].sentiment.polarity
                        if nominee not in match_count_dict[full_award_name]:
                            match_count_dict[full_award_name][nominee] = 1
                            sentiment_polarity_dict[full_award_name][nominee] = []
                            sentiment_polarity_dict[full_award_name][nominee].append(polarity)
                        else:
                            match_count_dict[full_award_name][nominee] += 1
                            sentiment_polarity_dict[full_award_name][nominee].append(polarity)
        else: # Word "wins" not in tweet
            tweet_nominees = ""
            tweet_award = ""
    return (match_count_dict, sentiment_polarity_dict)

# Function to find the nominee winner based on the "votes", and link in the average tweet sentiment of them winning
def identify_winner(match_count_dict, sentiment_polarity_dict):
    winners = {}
    for award_key in match_count_dict.keys():
        sentiments = sentiment_polarity_dict[award_key]
        award_votes = match_count_dict[award_key]
        nominee_winner = ""
        max_votes = 0
        for nominee in award_votes.keys():
            if award_votes[nominee] > max_votes:
                max_votes = award_votes[nominee]
                nominee_winner = nominee
        if nominee_winner:
            average_polarity = round(sum(sentiments[nominee_winner]) / len(sentiments[nominee_winner]), 2)
        else:
            average_polarity = ''
        winners[award_key] = {}
        winners[award_key]['winner'] = nominee_winner
        winners[award_key]['average_polarity'] = average_polarity
    return winners