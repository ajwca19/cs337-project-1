Instructions on what file(s) to run, what packages to download / where to find them, how to install them, etc., and any other necessary information.

Our team's GitHub repo can be found at https://github.com/ajwca19/cs337-project-1

Non-standard packages used in code:
nltk - https://www.nltk.org/install.html ( pip install nltk )
Wikipedia-API - https://pypi.org/project/Wikipedia-API/ ( pip install wikipedia-api ) 
imdbPY - https://pypi.org/project/IMDbPY/ ( pip install imdbPY )
spaCy -https://spacy.io/usage ( pip install spacy )
spaCy TextBlob (pip install spacytextblob)
TextBlob (pip install textblob)
pandas - https://pandas.pydata.org/ ( pip install pandas )
Gensim (used for word2vec) - (pip install word2vec)

All grading can be done through running the functions in gg_api.py. Each individual function other than main() and pre_ceremony() calls on a file containing a solution to each sub-problem as presented in the project outline.

Pre_ceremony() should ALWAYS be run before any individual function, but it's called in main().

The only function whose input is dependent on another's output is get_winners(), which uses a nominees list defined as a global variable in the body of get_nominees(). All functions are currently hardcoded to use the official awards list, but this could be modified to use our own list of awards as desired simply by replacing mentions of "OFFICIAL_AWARDS_1315" with the global variable "awards". Our code from start to finish takes me about 6-7 minutes to run.

IMPORTANT: We have seen an error once or twice that is from the Wikipedia api that we use. It's not replicable, nor does it occur every time. Looking online, it seems like it results from factors outside of our control. If this happens, try running the code again and it should fix the problem - if it continues to occur, please tell us!!!!
=======
The only function whose input is dependent on another's output is get_winners(), which uses a nominees list defined as a global variable in the body of get_nominees(). All functions are currently hardcoded to use the official awards list, but this could be modified to use our own list of awards as desired simply by replacing mentions of OFFICIAL_AWARDS_1315 with the global variable "award"

THOUGHT PROCESSES BEHIND INDIVIDUAL SUB-PROCESSES:
pre_ceremony()/preprocessing: reads tweets into a dataframe used in the rest of the problems. Also separates tweets out into buckets to prevent having to go through all 140k tweets over and over again.

host names: filters tweets to limit those that mention a word form of the lemma "host". These tweets are then parsed using spaCy's built-in parser and individual peoples' names are extracted. These are clustered by checking for matching tokens and determining that the most popular mention of a name is likely the most "official" representation. Certain use-cases of the word "host" and "hosts" are examined to determine how many hosts there are (=1 or >1), then host(s) is/are determined by popularity in mentions.

award names: filters tweets to limit those that mention "nominated for best" or "wins best". Removes all possible words appearing in the top 10 hashtags, and cleans the filtered tweets to remove unnecessary information. Out of the cleaned and filtered tweets, created word embeddings and clustered the embeddings into 25 clustered to represent clusters of possible award phrases. Finally, selected the most frequently mentioned possible award phrase from each cluster, if the phrase was mentioned at least twice. These selected phrases were inferred to be the award names.

<<<<<<< HEAD
presenters, mapped to awards: filters tweets with one of the essential keywords that may suggest a potential presenter. Further parsed by changing words with all caps into only first letter caps, using spaCy's entity recognition parser, using wikipedia API to send a query to the wikipedia server to determine if the extracted word is an existing person and using IMDB to check if a movie is an existing movie to increase accuracy. After changing the type to dictionary, count it again according to the frequency of appearance of each word in the sentence, and sort it using a python function called nlargest, and remove keywords that appear less frequently. The last keywords and the remaining words after removing stopwords from the award list are made into a list, and after matching them in each sentence, match the award and nominee with the highest frequency.
=======
>>>>>>> 6afc3b1a0c4a62090ad0bda7af016abbe943e03b

nominees, mapped to awards: filters tweets with one of the essential keywords that may suggest a potential nominee and with the word "best". Further parsed by changing words with all caps into only first letter caps, using spaCy's entity recognition parser, using wikipedia API to send a query to the wikipedia server to determine if the extracted word is an existing person and using IMDB to check if a movie is an existing movie to increase accuracy. After changing the type to dictionary, count it again according to the frequency of appearance of each word in the sentence, and sort it using a python function called nlargest, and remove keywords that appear less frequently. The last keywords and the remaining words after removing stopwords from the award list are made into a list, and after matching them in each sentence, match the award and nominee with the highest frequency.

winners, mapped to awards: winners takes in the list of nominees from the previous solutions. Removes stopwords from tweets and then, using a list of provided award names, tries to identify if a tweet is referring to a particular award by counting the number of words from the award name are mentioned in the tweet (the award with the max number of words mentioned wins). If a tweet was matched to an award name, then the tweet is searched to see if a nominee's name is mentioned prior to the word "wins". A count is kept to tally how often nominee's names are mentioned. The nominee with the max count is inferred to be the winner, matched to the award category inferred from the tweet.


ADDITIONAL FUNCTIONALITY:

fashion: extracts all tweets related to fashion, the red carpet, and celebrities outfits, then measures average sentiment and popularity to figure out who's talking about the best and worst dressed of the night. Outputs results based on relative mentions in the tweets.

sentiment of winners: If a tweet mentioned an award and nominee (see winners, mapped to awards), the sentiment (polarity) of the tweet was saved in a list. Once the final winner was inferred, the sentiment of each tweet related to the winner and award category was averaged, to provide an average sentiment of that individual winning that particular award.
