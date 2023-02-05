#importing necessary modules - pandas, nltk, regex, spacy, and RNG
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import re
import math
import random
import spacy
from spacy import displacy
from spacytextblob.spacytextblob import SpacyTextBlob
from collections import Counter
import en_core_web_sm

nlp = en_core_web_sm.load()
nltk.download("punkt")
nlp.add_pipe('spacytextblob')

def best_worst_dressed(fashion_tweets):
    #TAG ENTITIES
    entities_counts = {} #dictionary with key: entity name and value: number of appearances in tweets
    entities_clusters = {} #dictionary with key: entity name and value: name of "representative" entity
    entities_polarities = {}
    parsed_tweets = []
    for tweet in tweets_with_fashion_mention:
        parsed_tweet = nlp(tweet)
        parsed_tweets.append(parsed_tweet)
        for entity in parsed_tweet.ents:
            if entity.label_ == "PERSON" and re.match("[a-zA-Z0-9\.'’+-_@/]+", entity.text) and not re.search("\(|\)", entity.text):
                person = entity.text
                if person in entities_clusters:
                    entities_polarities[person] = (entities_counts[person] * entities_polarities[person] + parsed_tweet._.blob.polarity) / (entities_counts[person] + 1) 
                    entities_counts[person] += 1
                else:
                    entities_counts[person] = 1
                    entities_polarities[person] = parsed_tweet._.blob.polarity
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
    #entities_clusters
    #entities_to_remove

    #combine counts in the entity_counts dictionary
    for non_rep in entities_to_remove:
        if entities_clusters[non_rep] in entities_counts:
            entities_polarities[entities_clusters[non_rep]] = (entities_polarities[entities_clusters[non_rep]] * entities_counts[entities_clusters[non_rep]] + entities_polarities[non_rep] * entities_counts[non_rep])/(entities_counts[entities_clusters[non_rep]] + entities_counts[non_rep])
            entities_counts[entities_clusters[non_rep]] += entities_counts.pop(non_rep)

    #entities_polarities
    vote_distribution = list(entities_counts.values())
    average_count = sum(vote_distribution)/len(vote_distribution)
    fashion_icons = []
    for candidate in entities_counts:
        if entities_counts[candidate] >= average_count:
            fashion_icons.append(candidate)
    fashion_icons = sorted(fashion_icons, key = lambda e : entities_counts[e] * entities_polarities[e], reverse = True)
    fashion_scores = {}
    for icon in fashion_icons:
        fashion_scores[icon] = entities_counts[icon] * entities_polarities[icon]
    best_dressed = []
    worst_dressed = []
    for i in range(0, len(fashion_icons) - 1):
            if fashion_scores[fashion_icons[i + 1]] / fashion_scores[fashion_icons[i]] < 0.75:
                best_dressed = fashion_icons[:i+1]
                break
    for i in range(1, len(fashion_icons) - 1):
            if fashion_scores[fashion_icons[-1 * (i + 1)]] >= 0 or fashion_scores[fashion_icons[-1 * (i + 1)]] / fashion_scores[fashion_icons[-1 * i]] < 0.75:
                worst_dressed = fashion_icons[-1*(i+1):]
                break
    return (best_dressed, worst_dressed)