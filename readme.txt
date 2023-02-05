Instructions on what file(s) to run, what packages to download / where to find them, how to install them, etc., and any other necessary information.

Non-standard packages used in code:
nltk - https://www.nltk.org/install.html ( pip install nltk )
Wikipedia-API - https://pypi.org/project/Wikipedia-API/ ( pip install wikipedia-api ) 
imdbPY - https://pypi.org/project/IMDbPY/ ( pip install imdbPY )
spaCy -https://spacy.io/usage ( pip install spacy )
pandas - https://pandas.pydata.org/ ( pip install pandas )

All grading can be done through running the functions in gg_api.py. Each individual function other than main() and pre_ceremony() calls on a file containing a solution to each sub-problem as presented in the project outline.

Pre_ceremony() should ALWAYS be run before any individual function, but it's called in main().
The only function whose input is dependent on another's output is get_winners(), which uses a nominees list defined as a global variable in the body of get_nominees(). All functions are currently hardcoded to use the official awards list, but this could be modified to use our own list of awards as desired simply by replacing mentions of OFFICIAL_AWARDS_1315 with <INSERT VARIABLE NAME HERE THIS IS IMPORTANT>

THOUGHT PROCESSES BEHIND INDIVIDUAL SUB-PROCESSES:
pre_ceremony()/preprocessing: reads tweets into a dataframe used in the rest of the problems.
host names: filters tweets to limit those that mention a word form of the lemma "host". These tweets are then parsed using spaCy's built-in parser and individual peoples' names are extracted. These are clustered by checking for matching tokens and determining that the most popular mention of a name is likely the most "official" representation. Certain use-cases of the word "host" and "hosts" are examined to determine how many hosts there are (=1 or >1), then host(s) is/are determined by popularity in mentions.
award names:
presenters, mapped to awards:
nominees, mapped to awards:
winners, mapped to awards: winners takes in the list of nominees from the previous solutions. 


ADDITIONAL FUNCTIONALITY:
