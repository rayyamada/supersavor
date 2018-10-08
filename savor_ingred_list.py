# savor_ingred_list.py
#
# - this script reads in the nouns_list  (list of all unigram ingredients)
#   and generates bigrams and trigrams from them.  The most common ingredients
#   appearing at least 1% of the time are kept.  The list with uni,bi,and trigrams
#   is saved in  ingredients_list.csv
#
#   NOTE: this script and savor_nouns.py  only need to be run once for learning
#         from the data.  The live webapp need not use these two scripts.
#
#--------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import re
import matplotlib.pyplot as plt

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

import nltk
from nltk.tokenize import word_tokenize

import collections  # for sorting list by items that appear most frequently

import os.path



# read in nouns list (ie. list of all unigram ingredients)
nouns = pd.read_csv("nouns.csv")
nouns_list = list(nouns.iloc[:,0])
cat_list   = list(nouns.iloc[:,1])   # category: F,V,M,P,S,D,O 


stoplist_numbers      = [str(i) for i in range(1001)]
stoplist_measurements = ['basket', 'bunch',
                        'cm', 'centimeter', 'centimeters',
                        'cup','cups',
                        'cut','cuts',
                        'gal','gallon','gallons',
                        'half','halves',
                        'head','heads',
                        'inch','inches',  
                        'ml',
                        'ounce', 'ounc', 'ounces',  'oz',
                        'pack', 'packs',
                        'piece', 'piec','pieces', 'pint', 'pints', 'pinch',
                        'pound', 'pounds', 'lb', 'lbs',
                        'qt', 'quart', 'quarter','quarters',
                        'slice','slices','slic',
                        'sprig','sprigs','stick','sticks',
                        'teaspoon','teaspoons','tablespoon','tablespoons',
                        'tsp','tsps','tbsp','tbsps',
                        ]

extrawords = ['low','salt','sodium','unsalted','reduced']
removelist = stoplist_numbers + stoplist_measurements + extrawords



# read json
df_epi = pd.read_json('epicurious-recipes-with-rating-and-nutrition/full_format_recipes.json')

df2 = df_epi.loc[:,['ingredients','title']]

# cleaning data - missing ingredients list
temp = []
for i in range(df2.shape[0]):
    if type(df2.ingredients[i]) != list:   # nan value
        temp.append(i)
                
df2 = df2.drop(temp)  
n_recipes = df2.shape[0]



# 1. concatenate ingredients items from all recipes into one long list
#     each ingredient item (string of text) is one element in the list
full_list = []

for i in range(df2.shape[0]):
    ii = df2.index[i]
    if type(df2.ingredients[ii]) != list:
        continue  # skip this item if missing data
    full_list = full_list + df2.ingredients[ii]

# 2. process full_list 
#  - remove endings like 's' and 'es'  and convert 'ies' to 'y'

#  ( not happy with stemmer from nltk
#    removes things like 'able' from 'vegetable' and 'ed' from 'dried'  )

# CountVectorizer removes the hyphens between words  things like '1/2' also disappear
#   note:  CountVectorizer makes everything lower case


for i in range( len(full_list) ):
    item = full_list[i].split()
    
    item = [re.sub(',$','',word) for word in item]        # remove commas
    item = [re.sub('\(|\)','',word) for word in item]     # remove parentheses

    #item = [re.sub('ves$','f',word) for word in item]    # messes up 'cloves' to 'clof'
    item = [re.sub('ies$','y',word) for word in item] 
    item = [re.sub('s$|es$','',word) for word in item]   #  'slices' to 'slic'
    
    item = [re.sub('\d+\/\d+','',word) for word in item]  # remove fractions
    item = [re.sub('^\d+','',word) for word in item]   # remove numbers
    
    full_list[i] =  ' '.join(item)
    




# ----- generate ingredients list ------

filename = 'ingredients_list.csv'

# write header, if file does not exist   
#if not os.path.isfile(filename):
#    f = open(filename, 'w')
#    f.write("%s\n" % 'item_name')
#    f.close()

# write list items to file
f = open(filename, 'w')

headers = 'item_name,type\n'
f.write(headers)

for k in range(len(nouns_list)):   # for each unigram ingredient, generate bigrams and trigrams 
						  # and save to ingredients_list

	item = nouns_list[k]	
	cat  = cat_list[k]					  
	print(item)						  

	corpus = []           # create a corpus containing all recipe lines containing 'item'
	searchword = item

	for i in range(len(full_list)):
	    if re.search(searchword, full_list[i] ):  # if searchword appears in ingredient item
	    	corpus.append(full_list[i])           # add this ingredient item to corpus



	ngram_list = []

	# for each item in corpus, add its bi- and trigrams to the list 'ngram_list'
	for item in corpus:
	    temp = list(nltk.ngrams( item.split(), 2 ))
	    bigram_list = [' '.join(tup) for tup in temp
	                   if re.search('\s'+searchword+'\s?|\s?'+searchword+'\s', ' '.join(tup) )]
	                   # need these \s otherwise a word like "paste" will be found in 'unpasteurized'
	    
	    temp = list(nltk.ngrams( item.split(), 3 ))
	    trigram_list = [' '.join(tup) for tup in temp 
	                    if re.search('\s'+searchword+'\s?|\s?'+searchword+'\s', ' '.join(tup) )]
	    
	    ngram_list = ngram_list + bigram_list + trigram_list
	    
	    # need to clean ngram_list  (remove *, (,), etc ... )
	    ngram_list = [' '.join(re.findall('\b?\w\w+\b?',w)) for w in ngram_list ] 



	# -keep only the words that are nouns and adjectives.  Remove words like "finely", "chopped", etc
	# -also remove words that are in removelist (like 'tablespoon', 'cup', etc.)
	ngram_list2 = []
	for i in range(len(ngram_list)):
	    tagged_test = nltk.pos_tag( ngram_list[i].split() )
	    words = ' '.join([word.lower() for word,pos in tagged_test if (pos == 'NN' or pos=='JJ') and 
	                      (word not in removelist) ])
	    if (len(words)>0) and ( searchword in words.split() ):
	        ngram_list2.append(words)



	counter = collections.Counter(ngram_list2)

	if len(counter.most_common()) != 0:
		if counter.most_common()[0][0] == searchword:  # most common item is the unigram searchword
		    tempno = counter.most_common()[0][1]
		else:
		    tempno = 0
		    
		cutoff = (len(ngram_list2)-tempno) * 0.01    # keep words that appear in at least 1% of recipes


		cutoff_list = [searchword]
		if tempno == 0:  # first item in list is not searchword
		    cutoff_list.append(counter.most_common()[0][0])
		for i in range(1, min( len(ngram_list2), len(counter.most_common()) )):
		    if counter.most_common()[i][1] > max(cutoff,9):   # should at least 10 times
		        cutoff_list.append(counter.most_common()[i][0])
		    else:
			    break


		# write items in cutoff_list to file  filename

		for item2 in cutoff_list:
			#f.write("%s\n" % item2)
			f.write(item2 + ',' + cat + '\n')

f.close()



# -----------------------------------------------------------------
#  trim list,  remove duplicates, remove items with nonsense words

list0 = pd.read_csv(filename)

list3 = list( zip(list0.iloc[:,0],list0.iloc[:,1]) )  # make list of tuples
list4 = list( set(list3) )  # convert list to set to remove duplicates
list4.sort()


remove_list = []

remove_wordlist = ['lengthwise','crosswise','halved','dozen','diameter',
				   'pinch','coarse',
				   'peeled','diced','grated','trimmed','torn',
                   'sometim','such','plu','bag','box','jar','package',
                   'accompaniment', 'other', 'peel',
                   'available','additional','preferably',
                   'room','temperature','optional',
                   'pan','thermometer','grinder','cutter','equipment',
                   'cardboard','market','quality'
                  ]

names = list(zip(*list4))[0]   # unpackages list of first elements of tuples
cats  = list(zip(*list4))[1]

for i in range(len(names)):

    # remove items which contain words in remove_wordlist
    if len( set(names[i].split()) & set(remove_wordlist) ) > 0:   # intersection of sets
        remove_list.append(i)
        
    # remove duplicates which only differ by cat.  Prioritize cat other than 'O'
    if i > 0:
        if names[i] == names[i-1]:  # duplicate
            if cats[i] == 'O':
                remove_list.append(i)
            else:
                remove_list.append(i-1)  # remove the first one (even though it might not be 'O')


names2 = [names[i] for i in range(len(names)) if i not in remove_list]
cats2  = [ cats[i] for i in range(len(names)) if i not in remove_list]



filename2 = 'ingredients_list_short.csv'

f = open(filename2, 'w')

headers = 'item_name,type\n'
f.write(headers)

for i in range(len(names2)):
    f.write(names2[i] + ',' + cats2[i] + '\n')

f.close()


# I would also remove unigram words 'beef','pork','chicken','lamb'  (too vague)
# also 'filet','fillet'




