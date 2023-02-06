Instructions on what file(s) to run, what packages to download / where to find them, how to install them, etc., and any other necessary information.

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
The only function whose input is dependent on another's output is get_winners(), which uses a nominees list defined as a global variable in the body of get_nominees(). All functions are currently hardcoded to use the official awards list, but this could be modified to use our own list of awards as desired simply by replacing mentions of "OFFICIAL_AWARDS_1315" with the global variable "awards"

THOUGHT PROCESSES BEHIND INDIVIDUAL SUB-PROCESSES:
pre_ceremony()/preprocessing: reads tweets into a dataframe used in the rest of the problems. Also separates tweets out into buckets to prevent having to go through all 140k tweets over and over again.

host names: filters tweets to limit those that mention a word form of the lemma "host". These tweets are then parsed using spaCy's built-in parser and individual peoples' names are extracted. These are clustered by checking for matching tokens and determining that the most popular mention of a name is likely the most "official" representation. Certain use-cases of the word "host" and "hosts" are examined to determine how many hosts there are (=1 or >1), then host(s) is/are determined by popularity in mentions.

award names: filters tweets to limit those that mention "nominated for best" or "wins best". Removes all possible words appearing in the top 10 hashtags, and cleans the filtered tweets to remove unnecessary information. Out of the cleaned and filtered tweets, created word embeddings and clustered the embeddings into 25 clustered to represent clusters of possible award phrases. Finally, selected the most frequently mentioned possible award phrase from each cluster, if the phrase was mentioned at least twice. These selected phrases were inferred to be the award names.

presenters, mapped to awards:

nominees, mapped to awards:

winners, mapped to awards: winners takes in the list of nominees from the previous solutions. Removes stopwords from tweets and then, using a list of provided award names, tries to identify if a tweet is referring to a particular award by counting the number of words from the award name are mentioned in the tweet (the award with the max number of words mentioned wins). If a tweet was matched to an award name, then the tweet is searched to see if a nominee's name is mentioned prior to the word "wins". A count is kept to tally how often nominee's names are mentioned. The nominee with the max count is inferred to be the winner, matched to the award category inferred from the tweet.


ADDITIONAL FUNCTIONALITY:

fashion: extracts all tweets mentioning some sort of red carpet outfit or dress, then runs popularity and sentiment analyses on them, clustering by entity. There's a cutoff of relative mentions that determine who had the best and worst looks of the night, which get printed out in a list.

sentiment of winners: If a tweet mentioned an award and nominee (see winners, mapped to awards), the sentiment (polarity) of the tweet was saved in a list. Once the final winner was inferred, the sentiment of each tweet related to the winner and award category was averaged, to provide an average sentiment of that individual winning that particular award.