# savor_base_prices.py
#
# This script tries to get non-sale prices for all ingredients in 'ingredients_list_short.csv'  
# from the online grocer.  These prices are needed for the budget estimator.
#
# This script does not need to be run every day or week, but just occasionally to update prices
# for seasons and inflation. 
#
#--------------------------------------------------------------------------------------------


import numpy as np
import pandas as pd
import re
#import matplotlib.pyplot as plt
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

import nltk
from nltk import ngrams

from savor import clean_item_text



main_list = pd.read_csv('ingredients_list_short.csv')

# -since currently we're only tracking fresh goods  (F,V,M,P,S) and not condiments, 
# dry goods, spices, etc...,  remove all ingredients of type O,MO,PO,SO  (O=other)
# -this will also save computation time by making the recipe matrix much smaller
main_list = main_list.drop( np.nonzero(
        (main_list.type=='O')|(main_list.type=='MO')|(main_list.type=='PO')|(main_list.type=='SO')
            )[0]
            )

main_list = main_list.reset_index().drop(['index'],axis=1)


n_items = main_list.shape[0]    # number of items in our "list of ingredients"

ingred_list = list(main_list.item_name.values)



poultry = pd.read_csv('allnorm_poultry.csv')
meat = pd.read_csv('allnorm_meat.csv')
vegetables = pd.read_csv('allnorm_vegetables.csv')
fruits = pd.read_csv('allnorm_fruits.csv')
seafood = pd.read_csv('allnorm_seafood.csv')


df = fruits.append(vegetables).append(poultry).append(meat).append(seafood)
df = df.reset_index(drop=True)
df = df.drop(columns=['Unnamed: 0', 'freshness_rating','units_descr'])


#---------------------------------
# BASE PRICE VECTOR ENCODER
#---------------------------------
#
# -create a dataframe base_vec with the number of rows equal to n_items 
# (length of our "list of ingredients")
# -for each item, we will try to find an item from our base list (df) that fits that item type
# -if multiple items fit, we will choose the cheapest find.
#
# algorithmically, 
# - for each item in ingred_list, see if it matches a bi- or tri-gram of item from base list (df).
#   If it matches, then it will be logged.  If another match is found, then the cheaper of the 
#   two items will be taken (since everything has been normalized by lbs).  
#   If another item matches but it is using 'ea' (each) instead of 'lb' then swap it. 
#
#     If no bigrams or trigrams are matched, then we will match unigrams.
#
#  base_vec  - contains all items in ingred_list and their corresponding best match from the
#              items found in df.  Will also show corresponding, sku_code, orig_price,
#              and units_soldas

base_vec = pd.DataFrame({ 'ingredient'   : ingred_list,
                          'item_name'    : '',
                          'sku_code'     : '',
                          'orig_price'   : 0.0,
                          'units_soldas' : ''
                        } )

n_items = len(df)
bool_vec  = np.zeros(len(ingred_list), dtype=bool) 

remove_adjs = [ 'small','medium','large', 'fresh','ripe',
                'thick','thin', 'live'
              ]


# for each item in ingred_list, find its best fit in df
for k in range(len(ingred_list)):  
    
    for i in range(n_items):    # for each item in df 
        name = df.item_name[i].lower()
        
        # from sale item name create unigram,bigram,trigram lists
        unigram_list = clean_item_text(name).split() # clean list

        temp = list(ngrams( unigram_list, 2 ))
        bigram_list = [' '.join(tup) for tup in temp]

        temp = list(ngrams( unigram_list, 3 ))
        trigram_list = [' '.join(tup) for tup in temp]
        
        
        if ingred_list[k] in (bigram_list + trigram_list):  # any matching 2,3-grams?
            
            # check if another df item has already been found
            #  -if no, move df item data into base_vec dataframe
            #  -if yes, compare which price is better and possibly replace
            if bool_vec[k] == False:  # no sale item has been found for this ingred yet
                base_vec.loc[k,'item_name']    = df.item_name[i]
                base_vec.loc[k,'sku_code']     = df.sku_code[i]
                base_vec.loc[k,'orig_price']   = df.orig_price[i]
                base_vec.loc[k,'units_soldas'] = df.units_soldas[i]
                bool_vec[k] = True
            else: # compare with existing
                if (base_vec.units_soldas[k] != 'lb') and \
                   (      df.units_soldas[i] == 'lb'):
                    base_vec.loc[k,'item_name']  = df.item_name[i]
                    base_vec.loc[k,'sku_code']   = df.sku_code[i]
                    base_vec.loc[k,'orig_price'] = df.orig_price[i]
                    base_vec.loc[k,'units_soldas']    = df.units_soldas[i]  
                        
                elif (base_vec.units_soldas[k] == 'lb') and \
                     (      df.units_soldas[i] != 'lb'):
                    # do nothing
                    foo32 = 2
                    
                else:  # either both 'lb' or both something else
                    if df.orig_price[i] < base_vec.orig_price[k]:  # better deal, replace item
                        base_vec.loc[k,'item_name']  = df.item_name[i]
                        base_vec.loc[k,'sku_code']   = df.sku_code[i]
                        base_vec.loc[k,'orig_price'] = df.orig_price[i]
                        base_vec.loc[k,'units_soldas']    = df.units_soldas[i] 
        
    
    # if after searching bi- and tri-grams, no match is not found yet, then search
    # unigrams and bigrams.  Here we will also remove adjectives, e.g. 'large carrot'
    # in ingred_list will become  'carrot'
    if bool_vec[k] == False:
        
        # remove adjs from ingred_list[k]  (all adjectives is too many, some are important)
        #tagged = nltk.pos_tag(ingred_list[k].split())
        #nouns = [word for word,pos in tagged if (pos == 'NN' or pos=='NNS') ] 
        #nouns = ' '.join(nouns)
        
        nouns = [word for word in ingred_list[k].split() if word not in remove_adjs]
        nouns = ' '.join(nouns)
        
        for i in range(n_items):    # for each item in df 
            name = df.item_name[i].lower()
            
            unigram_list = clean_item_text(name).split() # clean list

            temp = list(ngrams( unigram_list, 2 ))
            bigram_list = [' '.join(tup) for tup in temp]

            if nouns in (unigram_list + bigram_list): 
                if bool_vec[k] == False:  # no sale item has been found for this ingred yet
                    base_vec.loc[k,'item_name']    = df.item_name[i]
                    base_vec.loc[k,'sku_code']     = df.sku_code[i]
                    base_vec.loc[k,'orig_price']   = df.orig_price[i]
                    base_vec.loc[k,'units_soldas'] = df.units_soldas[i]
                    bool_vec[k] = True
                else: # compare with existing
                    if (base_vec.units_soldas[k] != 'lb') and \
                       (      df.units_soldas[i] == 'lb'):
                        base_vec.loc[k,'item_name']  = df.item_name[i]
                        base_vec.loc[k,'sku_code']   = df.sku_code[i]
                        base_vec.loc[k,'orig_price'] = df.orig_price[i]
                        base_vec.loc[k,'units_soldas']    = df.units_soldas[i]  

                    elif (base_vec.units_soldas[k] == 'lb') and \
                         (      df.units_soldas[i] != 'lb'):
                        # do nothing
                        foo32 = 2

                    else:  # either both 'lb' or both something else
                        if df.orig_price[i] < base_vec.orig_price[k]:  # better deal, replace item
                            base_vec.loc[k,'item_name']  = df.item_name[i]
                            base_vec.loc[k,'sku_code']   = df.sku_code[i]
                            base_vec.loc[k,'orig_price'] = df.orig_price[i]
                            base_vec.loc[k,'units_soldas']    = df.units_soldas[i]

#print(k)  # check if it made it to last iteration  


#  save to .csv
# -since base_vec does not include sales prices but original prices, it need NOT be 
#  updated frequently

base_vec.to_csv('base_price_vec.csv')





