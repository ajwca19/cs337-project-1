import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re
import random
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm

nlp = en_core_web_sm.load()
nltk.download("punkt")

# get_names(pandas DataFrame, string) -> listof(string)
# get_names() takes in a DataFrame containing pre-processed tweets
# and the name of the awards show, then uses both to find the name(s)
# of the likely host(s) of the show. Regardless of number of hosts,
# returns a list containing the name(s) of the host(s).
def get_names(tweets, ceremony_name):
    
    #start by extracting relevant tweets' text: eliminate retweets and only add tweets with a form of "host"
    tweets_with_host = [] #list of strings containing the word "host", "hosts", "hosting", "hosted", etc.
    hashtag_re = "#[a-zA-Z0-9_]+" #regex to remove hashtags from the data
    for i in range(0, len(tweets)):
        tweet_text = tweets.loc[i]['text']
        if re.search("host(s*)", tweet_text.lower()) and not re.search("^[Rr][Tt]", tweet_text):
            cleaned_text = re.sub(hashtag_re, "", tweet_text)
            tweets_with_host.append(cleaned_text)
    
    #then parse the tweets with spacy to get relevant information
    parsed_tweets = map(nlp, tweets_with_host)
    
    cluster_output = cluster_entities(parsed_tweets)
    entities_counts = cluster_output[0] #dictionary with key: entity name and value: number of appearances in tweets
    entities_clusters = cluster_output[1] #dictionary with key: entity name and value: name of "representative" entity
    
    are_multiple_hosts = number_of_hosts(parsed_tweets)
    
    host_names = find_likely_hosts(entities_counts, are_multiple_hosts)
    
    return host_names
    

    
# ------- helper functions below this line can maybe be moved elsewhere if we want --------

# cluster_entities(listof(spacy Doc)) -> ({string: integer}, {string: string})
# cluster_entities counts unique entity appearances in the tweets, then clusters
# using an algorithm similar to a union_find
# returns 2 dictionaries mapping from 1) clustered entity names to number of combined mentions
# and 2) all entity names mapped to representative entities
def cluster_entities(parsed_tweets):
    entities_counts = {} #dictionary with key: entity name and value: number of appearances in tweets
    entities_clusters = {} #dictionary with key: entity name and value: name of "representative" entity
    for parsed_tweet in parsed_tweets:
        for entity in parsed_tweet.ents:
            if entity.label_ == "PERSON" and re.match("[a-zA-Z0-9\.'’+-_@/]+", entity.text):
                person = entity.text
                if person in entities_clusters:
                    entities_counts[person] += 1
                else:
                    entities_counts[person] = 1
                    entities_clusters[person] = person
                    

    entities_to_remove = set()
    for entity_a in entities_clusters:
        #print("\n\n\n ENTITY A: " + entity_a)
        for entity_b in entities_clusters:
            #print("\n ENTITY B: " + entity_b + "\n_____________\n")
            if entities_counts[entity_a] >= entities_counts[entity_b]:
                #entity a is more popular than entity b
                entity_a_tokens = entity_a.split(" ")
                entity_b_tokens = entity_b.split(" ")
                for entity_a_token in entity_a_tokens:
                    #print("entity a token: " + entity_a_token)
                    if len(entity_a_token) >= len(entity_b) and re.search(entity_a_token, entity_b):
                        #entities are a match! cluster them accordingly
                        #print("clustering: " + entity_b + " in group led by " + entities_clusters[entity_a] + "\n")
                        entities_clusters[entity_b] = entities_clusters[entity_a]
                        entities_to_remove.add(entity_b)
                        break
                for entity_b_token in entity_b_tokens:
                    #print("entity b token:" + entity_b_token)
                    if len(entity_b_token) >= len(entity_a) and re.search(entity_b_token, entity_a):
                        #entities are a match! cluster them accordingly
                        #print("clustering: " + entity_b + " in group led by " + entities_clusters[entity_a] + "\n")
                        entities_clusters[entity_b] = entities_clusters[entity_a]
                        entities_to_remove.add(entity_b)
                        break

    #combine counts in the entity_counts dictionary
    for non_rep in entities_to_remove:
        entities_counts[entities_clusters[non_rep]] += entities_counts.pop(non_rep)
    
    #return the dictionaries
    return (entities_counts, entities_clusters)

# number_of_hosts(listof(spacy Doc)) -> boolean
# number_of_hosts sees if language implies that there are one or more than one hosts for the show
# returns True if number of hosts is MORE than one, False if number of hosts is EXACTLY one
def number_of_hosts(parsed_tweets):
    host_as_verb = [] #list of all tweets with host/hosts/hosting as a verb
    host_as_noun = [] #list of all tweets with host/hosts as a noun
    host_singular = 0 #count of all tweets implying a single host
    host_plural = 0 #count of all tweets implying more than one host
    for tweet in parsed_tweets:
        for token in tweet:
            if re.search("host", token.text.lower()):
                if token.pos_ == "VERB":
                    host_as_verb.append(tweet)
                    if token.text.lower() == "host":
                        host_plural += 1
                    elif token.text.lower() == "hosts":
                        host_singular += 1
                    break
                elif token.pos_ == "NOUN":
                    host_as_noun.append(tweet)
                    if token.text.lower() == "hosts":
                        host_plural += 1
                    elif token.text.lower() == "host":
                        host_singular += 1
                    break
    return host_plural >= host_singular

# find_likely_hosts({string: integer}, boolean) -> listof(string)
# find_likely_hosts finds the most popular host or hosts
# returns their name(s) in a list
def find_likely_hosts(candidates, host_number):
    if host_number == False: #singular case
        likely_host = ""
        likely_host_count = 0
        for candidate in candidates:
            if candidates[candidate] >= likely_host_count:
                likely_host = candidate
                likely_host_count = candidates[candidate]
        return [likely_host]
    else: #plural case
        vote_distribution = list(candidates.values())
        average_count = sum(vote_distribution)/len(vote_distribution)
        likely_hosts = []
        for candidate in candidates:
            if candidates[candidate] >= average_count:
                likely_hosts.append(candidate)
        likely_hosts = sorted(likely_hosts, key = lambda e : candidates[e], reverse = True)
        #must be at least 2 hosts - start cutoffs at index 1
        for i in range(1, len(likely_hosts) - 1):
            if candidates[likely_hosts[i + 1]] / candidates[likely_hosts[i]] < 0.5:
                likely_hosts = likely_hosts[:i+1]
                break
        return likely_hosts
    