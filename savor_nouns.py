# savor_nouns.py
#
# - this script is where the "topics" (recipe ingredient categories) are learned from
#   the recipe database.  
# - here a list of unigrams containing the most important ingredient nouns is generated
# - we've chosen a very small min_df=0.00025, so as to capture even rare ingredients
# - nouns relating to measurements (eg. 'cups','teaspoons', etc...) are removed as stopwords
#
# - after this script is run, run savor_ingred_list.py to generate bigrams and trigrams
#
#   NOTE: this script and savor_ingred_list.py  only need to be run once for learning
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


# read json
df_epi = pd.read_json('epicurious-recipes-with-rating-and-nutrition/full_format_recipes.json')

df2 = df_epi.loc[:,['ingredients','title']]

# cleaning data - missing ingredients list
temp = []
for i in range(df2.shape[0]):
    if type(df2.ingredients[i]) != list:
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



# stop word lists

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


stoplist = stoplist_numbers + stoplist_measurements + list(ENGLISH_STOP_WORDS)


# here we split the dataset into eight and then compute four separate (largely overlapping)
# vocabularies.  We do this because sometimes a word like 'potato' is picked up as an adjective
# instead of a noun.  We will take the union of the nouns (without repetition) from the eight
# vocabularies.

mindf=0.00025

vect1 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect1.fit( full_list[0:25000] )
vect2 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect2.fit( full_list[25000:50000] )
vect3 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect3.fit( full_list[50000:75000] )
vect4 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect4.fit( full_list[75000:100000] )
vect5 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect5.fit( full_list[100000:125000] )
vect6 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect6.fit( full_list[125000:150000] )
vect7 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect7.fit( full_list[150000:175000] )
vect8 = CountVectorizer(min_df=mindf,ngram_range=(1,1), stop_words=stoplist)
vect8.fit( full_list[175000:200000] )


tagged1 = nltk.pos_tag(vect1.vocabulary_)
tagged2 = nltk.pos_tag(vect2.vocabulary_)
tagged3 = nltk.pos_tag(vect3.vocabulary_)
tagged4 = nltk.pos_tag(vect4.vocabulary_)
tagged5 = nltk.pos_tag(vect5.vocabulary_)
tagged6 = nltk.pos_tag(vect6.vocabulary_)
tagged7 = nltk.pos_tag(vect7.vocabulary_)
tagged8 = nltk.pos_tag(vect8.vocabulary_)

nouns1 = [word for word,pos in tagged1 if (pos == 'NN' or pos=='NNS') ]
nouns2 = [word for word,pos in tagged2 if (pos == 'NN' or pos=='NNS') ]
nouns3 = [word for word,pos in tagged3 if (pos == 'NN' or pos=='NNS') ]
nouns4 = [word for word,pos in tagged4 if (pos == 'NN' or pos=='NNS') ]
nouns5 = [word for word,pos in tagged5 if (pos == 'NN' or pos=='NNS') ]
nouns6 = [word for word,pos in tagged6 if (pos == 'NN' or pos=='NNS') ]
nouns7 = [word for word,pos in tagged7 if (pos == 'NN' or pos=='NNS') ]
nouns8 = [word for word,pos in tagged8 if (pos == 'NN' or pos=='NNS') ]

nouns = list(set().union(nouns1,nouns2,nouns3,nouns4, \
                         nouns5,nouns6,nouns7,nouns8))   # use set to get union w/o repetition

nouns.sort()


filename = 'nouns.csv'
f = open(filename, 'w')

headers = 'item_name,type\n'
f.write(headers)

for noun in nouns:
    f.write(noun + ',' +  '\n')

f.close()


# we will have to add 'type' labels by hand.  From this rather short list of nouns
# the types will be carried over to the much longer ingredient list. 
#
#  Types:  'F' = Fruit
#          'V' = Vegetable
#          'M' = Meat
#          'P' = Poultry
#          'S' = Seafood
#          'D' = Dairy
#          'O' = Other




