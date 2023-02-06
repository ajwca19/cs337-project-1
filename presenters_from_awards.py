# Importing necessary modules 
import nltk
from nltk.corpus import stopwords
import re
import spacy
import pandas as pd
from heapq import nlargest
import wikipediaapi as wk
import imdb
import time

all_presenters_list = []

# Removing stopwords from the award list 
def remove_stopword_award_list(award_list):
    nltk.download('stopwords')
    stops = set(stopwords.words('english'))
    nltk_list = []

    for index, value in enumerate(award_list):

        for pos in nltk.pos_tag(nltk.word_tokenize(value)):

            if (pos[1].startswith("JJ") or pos[1].startswith("NN") or pos[1].startswith("RB") or pos[1].startswith(
                    "VB")) \
                    and ("'" not in pos[0]):

                ori_keyword = pos[0].strip().lower()

                if ori_keyword in stops:
                    continue
                if len(ori_keyword) < 3:
                    continue
            if ori_keyword not in nltk_list:
                nltk_list.append(ori_keyword)

    return nltk_list

# Deleting non-important information using regex
def cleansing_using_regex(tweets):

    http_pattern = re.compile("(\w+:\/\/\S+)")
    hash_pattern = re.compile("(#[A-Za-z0-9_]+)")
    amp_pattern = re.compile("&([0-9a-zA-Z]+)")
    tag_pattern = re.compile("(@[A-Za-z0-9_]+)")
    rt_pattern = re.compile("^[rR][tT] @[a-zA-Z0-9_]+: ")
    rt_pattern_2 = re.compile("RT")

    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)

    return_txt_list = []

    for i in tweets:

        v1 = re.sub(http_pattern, "", i)
        v2 = re.sub(hash_pattern, "", v1)
        v3 = re.sub(amp_pattern, "", v2)
        v4 = re.sub(rt_pattern, "", v3)
        v5 = re.sub(tag_pattern, "", v4)
        v6 = re.sub(emoji_pattern, "", v5)
        v7 = re.sub(rt_pattern_2, "", v6)
        v8 = re.sub(r"[^a-zA-Z_ ]", "", v7)

        if len(v8) > 2:
            return_txt_list.append(v8.strip())

    return list(set(return_txt_list))

# Identifying keywords and finding sentences where a presenter could be associated with an award 
def cleansing_finding_keyword(tweets, aw_word_list):

    keywords_1 = [  "presented", "presents", "presenting", "announcing", 
                    "introducing", "introduces"]
    keywords_2 = ["best"]
    keywords_3 = list(set(aw_word_list) - set(keywords_1) - set(keywords_2))

    return [txt for txt in tweets if 
            any(keyword in txt.lower() for keyword in keywords_1) 
        and any(keyword in txt.lower() for keyword in keywords_2) 
        and any(keyword in txt.lower() for keyword in keywords_3)]

# Fixing unncessarily capitalized expressions to uppercase at the beginning of the word 
def cleansing_remove_useless_capital(tweets):

    # nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')

    ret_list = []

    for txt in tweets:

        rev_txt = " ".join([i for i in txt.split(" ") if i != ""])
        lower_txt = ""

        for pos in nltk.pos_tag(nltk.word_tokenize(rev_txt)):

            keyword = pos[0]

            if not (pos[1].startswith("NN")) and pos[0].isupper() and len(pos[0]) != 1:
                keyword = pos[0].lower()

            if keyword.lower() == "tv":
                keyword = "television"
            lower_txt += (keyword + " ")

        ret_list.append(lower_txt.strip())

    return ret_list

# Extracting keywords that satisfy the criteria for person, organization, faciities, work of art, global and political entities
def cleansing_using_spacy_entity(tweets, search_type):

    # spacy.cli.download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")
    nlp.max_length = 10000000
    ent_dict = dict([(re.sub("[^a-zA-Z0-9\s]", "", str(x)), x.label_) for x in nlp(str(tweets)).ents])

    entity_list = []

    ceremony_name = "Golden Globes"
    ceremony_list = ceremony_name.lower().split(" ")

    if search_type == "PERSON":
        for k, v in ent_dict.items():
            if len(k.strip().split(" ")) == 2:
                if not any(c_word in k.lower() for c_word in ceremony_list):
                    if "best" not in k.lower() and "win" not in k.lower():
                        if v == "ORG" or v == "PERSON" or v == "WORK_OF_ART":
                            entity_list.append(k.lower())

    elif search_type == "MOVIE":
        for k, v in ent_dict.items():
            if len(k.strip().split(" ")) == 1:
                if not any(c_word in k.lower() for c_word in ceremony_list):
                    entity_list.append(k.lower())

    elif search_type == "ETC":
        for k, v in ent_dict.items():
            if len(k.strip().split(" ")) > 2:
                if not any(c_word in k.lower() for c_word in ceremony_list):
                    entity_list.append(k.lower())

    entity_list = list(set(entity_list))

    return entity_list

# Importing wikipedia and imdb modules to check if correct presenters exist 
def counting_name_and_match(tweets, entity_list, search_type, input_year):

    entity_dict = {key: 0 for key in entity_list}
    tweet = pd.DataFrame(tweets, columns=["text"])

    for k in entity_dict.keys():
        idx = tweet[tweet["text"].str.contains(k, case=False)]
        entity_dict[k] = len(idx)

    if search_type == "PERSON":
        per = int(len(entity_dict) * 0.75)
    elif search_type == "MOVIE":
        per = int(len(entity_dict) * 0.25)
    elif search_type == "ETC":
        per = int(len(entity_dict) * 0.1)

    str_list = nlargest(per, entity_dict, key=entity_dict.get)

    wiki_name_list = []
    movie_candidate_list = []
    wiki = wk.Wikipedia("en")

    if search_type == "PERSON":
        #print("Search_Type : ", search_type, "\nI'm searching for Wikipedia, so please wait while watching YouTube.")
        for k in str_list:
            try:
                k_wiki = "_".join(str(k).title().split(" ")).strip()
            except:
                time.sleep(10)
            else:
                k_wiki_page = wiki.page(k_wiki)
                w_cate = k_wiki_page.categories
                time.sleep(0.1)
                if len(w_cate) != 0:
                    w_cate = " ".join(list(w_cate.keys()))
                    if "disambiguaion" not in w_cate:
                        if search_type == "PERSON":
                            if ("actor" in w_cate) or ("actress" in w_cate) or ("director" in w_cate):
                                wiki_name_list.append(k_wiki_page.title)
                            elif (str(input_year) + " film" in w_cate) or ("television" in w_cate):
                                movie_candidate_list.append(k_wiki_page.title)
    elif search_type == "MOVIE":
        movie_candidate_list = str_list.copy()
    elif search_type == "ETC":
        movie_candidate_list = str_list.copy()

    wiki_name_list = list((set(wiki_name_list)))

    movie_name_list = []
    ia = imdb.Cinemagoer()

    #print("Search_Type : ", search_type, "\nI'm searching for IMDB, so please wait while watching YouTube.")
    for name in movie_candidate_list:
        ex = ""
        try:
            ex = ia.search_movie(str(name))
        except:
            time.sleep(10)
        else:
            time.sleep(0.1)
            if len(ex) != 0:
                for i in ex:
                    if name == i['title'].lower():
                        if 'year' in i.keys():
                            if int(i['year']) == int(input_year) - 1:
                                movie_name_list.append(name)
                                break

    movie_name_list = list(set(movie_name_list))
    movie_person_list = list(set(movie_name_list + wiki_name_list))
    movie_person_list_lower = [i.lower() for i in movie_person_list]


    entity_dict = {key: 0 for key in movie_person_list_lower}
    tweet = pd.DataFrame(tweets, columns=["text"])

    for k in entity_dict.keys():
        idx = tweet[tweet["text"].str.contains(k, case=False)]
        entity_dict[k] = len(idx)

    if search_type == "PERSON":
        per = int(len(entity_dict) * 0.9) 
    elif search_type == "MOVIE":
        per = int(len(entity_dict) * 0.9)
    elif search_type == "ETC":
        per = int(len(entity_dict) * 0.9) 

    entity_list = nlargest(per, entity_dict, key=entity_dict.get)

    return entity_list

# Mapping the presenters list to the award list 
def find_presenter_award_in_tweet(aw_list, aw_word_list, no_list, tweets):

    aw_dict = {k: [] for k in aw_list}
    no_dict = {k: {i: 0 for i in aw_word_list} for k in no_list}

    df = pd.DataFrame(tweets, columns=["text"])
    for i in no_dict.keys():
        # print(i)
        for j in df[df["text"].str.contains(i, case=False)]["text"].values.tolist():
            for k in no_dict[i].keys():
                if k in j.lower():
                    no_dict[i][k] += 1

    no_dict_1 = {k: {i: no_dict[k][i] for i in nlargest(7, no_dict[k], key=no_dict[k].get)} for k in no_dict}
    #print(no_dict_1)

    for k_1, v_1 in no_dict.items():

        for num in range(8, 1, -1):
            coinBool = False
            for award in aw_list:
                coincide = 0
                k_1_list = nlargest(num, v_1, key=v_1.get)
                if len(k_1.split(" ")) != 2:
                    if "actor" in k_1_list or "actress" in k_1_list or "director" in k_1_list:
                        break
                for word in k_1_list:
                    if word in award:
                        coincide += 1
                if coincide == num:
                    if len(k_1.split(" ")) != 2:
                        if "actor" in award or "actress" in award or "director" in award:
                            break
                    aw_dict[award].append(k_1)
                    coinBool = True
                    break
            if coinBool:
                break

    #print(aw_dict)
    print(pd.DataFrame(list(aw_dict.items()), columns=['Award_List', 'Presenter']))

    return aw_dict

def main(tweets, ceremony_name, year, aw_list):
    global all_presenters_list

    start_time = time.time()

    award_word_list = remove_stopword_award_list(aw_list)

    ###############################################################
    tweets_1 = cleansing_using_regex(tweets['text'].values.tolist())
    tweets_2 = cleansing_finding_keyword(tweets_1, award_word_list)
    tweets_3 = cleansing_remove_useless_capital(tweets_2)

    search_type = "PERSON" # A_B form
    entity_list = cleansing_using_spacy_entity(tweets_3, search_type)
    A_B_list = counting_name_and_match(tweets_3, entity_list, search_type, year)

    # search_type = "MOVIE"  # A form
    # name_list = cleansing_using_spacy_entity(tweets_3, search_type)
    # A_List = counting_name_and_match(tweets_3, name_list, search_type, year)

    # search_type = "ETC"  # A_B_C... form
    # name_list = cleansing_using_spacy_entity(tweets_3, search_type)
    # A_B_C_List = counting_name_and_match(tweets_3, name_list, search_type, year)

    Final_list = list(set(A_B_list))
    all_presenters_list = list(set(A_B_list))

    #print(time.time() - start_time)

    # Final_list = pd.read_csv("./nominee_Final.csv")["nominee"].values.tolist()
    award_presenter_dict = find_presenter_award_in_tweet(aw_list, award_word_list, Final_list, tweets_3)
    return award_presenter_dict