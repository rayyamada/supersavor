# savor_recipemat.py
#
# This script codifies in a matrix which ingredients are used in a recipe.  The rows of the 
# matrix are recipes and the columns are ingredients from ingredients_list_short.csv
#
# This script only needs to be run once and again only if the list of ingredients or recipe
# database changes. 
#
# The recipe matrix is saved to a file 'recipe_matrix.npz'
# A normalized recipe matrix (accounting for the amount of ingredients needed) is also saved.
#
#--------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import re

from nltk import ngrams
from savor import clean_item_text


# read recipe database  json 
df_epi = pd.read_json('epicurious-recipes-with-rating-and-nutrition/full_format_recipes.json')
df_epi = df_epi.loc[:,['ingredients','title','directions']]


df2 = df_epi.iloc[0:5000,:]    # FIRST, try use ONLY FIRST  N recipes
#df2 = df_epi


# cleaning data - missing ingredients list
temp = []
for i in range(df2.shape[0]):
    if type(df2.ingredients[i]) != list:
        temp.append(i)
        
        
df2 = df2.drop(temp)  
n_recipes = df2.shape[0]




# READ in  "list of ingredients"
#main_list = pd.read_csv('ingredients_list.csv')
main_list = pd.read_csv('ingredients_list_short.csv')


# -since currently we're only tracking fresh goods  (F,V,M,P,S) and not condiments, 
# dry goods, spices, etc...,  remove all ingredients of type O,MO,PO,SO  (O=other)
# -this will also save computation time by making the recipe matrix much smaller
main_list = main_list.drop( np.nonzero(
        (main_list.type=='O')|(main_list.type=='MO')|(main_list.type=='PO')|(main_list.type=='SO')
            )[0]
            )

main_list = main_list.reset_index().drop(['index'],axis=1)

ingred_list = list(main_list.item_name.values)

n_items = main_list.shape[0]    # number of items in our "list of ingredients"


index_F = np.nonzero(main_list.type=='F')[0]
index_V = np.nonzero(main_list.type=='V')[0]
index_M = np.nonzero(main_list.type=='M')[0]
index_P = np.nonzero(main_list.type=='P')[0]
index_S = np.nonzero(main_list.type=='S')[0]
index_D = np.nonzero(main_list.type=='D')[0]



#---------------------------------
# RECIPE MATRIX ENCODER
#---------------------------------
# - for each recipe, indicate in recipe matrix (boolean matrix, where each row is 
#   a different recipe and columns are item from "list of ingredients") 
#   whether a particular item is used.  
#      Items in recipe not found in our list are ignored.
# - given a recipe's ingredient item text, search it for trigrams, then bigrams, then unigrams.   
#   When a match is found STOP.  This way it will classify into the most specific category first.
#   E.g.  "cherry tomato" as opposed to just "tomato"
#   We also want to avoid multi-classification.  We don't want "cherry tomato" to also be 
#   logged as a "tomato" as well in the recipe matrix for a given recipe.

recipe_mat = np.zeros([n_recipes,n_items], dtype='bool')

for i in range(n_recipes):    # for each recipe  (each row of recipe matrix)
    i_ = df2.index[i]         # use i_ to correctly index dataframe
    item_list = df2.ingredients[i_]    # ingredients list for this recipe
    
    
    for j in range(len(item_list)):   # for each ingredient in this recipe
        item = item_list[j].lower()   # string containing ingredient #i
        item = clean_item_text(item)
        
        item_found = False    # boolean flagging if we found a match from ingred_list
                              # use this flag to prevent multiple matches for one ingredient line
        
        temp = list(ngrams( item.split(), 3 ))
        trigram_list = [' '.join(tup) for tup in temp]
        
        for k in range(n_items):  # for each item in main ingredient list  
            if ingred_list[k] in trigram_list:    # any matching trigrams?
                recipe_mat[i,k] = True            # update recipe matrix
                item_found = True
                break
                
                #item = item.replace(ingred_list[k],'')   # remove from list
                #temp = list(ngrams( item.split(), 3 ))   # modify trigram list
                #trigram_list = [' '.join(tup) for tup in temp]
        
        if item_found == False:
            temp = list(ngrams( item.split(), 2 ))    # generate bigrams from remaining words
            bigram_list = [' '.join(tup) for tup in temp]

            for k in range(n_items): 
                if ingred_list[k] in bigram_list:    
                    recipe_mat[i,k] = True
                    item_found = True
                    break
                    
                    #item = item.replace(ingred_list[k],'')   # remove from list
                    #temp = list(ngrams( item.split(), 2 ))   # modify bigram list
                    #bigram_list = [' '.join(tup) for tup in temp]
         
        unigram_list = item.split()   # generate unigrams from remaining words
        
        if item_found == False:
            for k in range(n_items): 
                if ingred_list[k] in unigram_list:    
                    recipe_mat[i,k] = True  
                    item_found = True
                    break
                    
                    #item = item.replace(ingred_list[k],'')
                    #unigram_list = item.split()
        
        
#print(i)  # check if it made it to last iteration   


#-----------------------------
# RECIPE MATRIX NORMALIZER
#-----------------------------
# To get a rough estimate of recipe prices, we utilize the following normalization procedure:
# - we assume recipe should be proportioned as servings for two, which is 1 lb of meat and 
#   1 lb of raw vegetables
# - ideally, we would compute exact recipe ratios based on the recipe, but ingredient
#   measurements used in recipes can be very different than how they are sold (e.g., 
#   recipe calls for 'eight leaves of cabbage' while cabbage is sold by the 'head').
# - the next phase of this project, should identify and match these exact quantities
# - for now we want to get a rough budget estimate, which will be accomplished by assuming that 
#   the 1 lb of meat is distributed uniformly across various meats that may appear in a recipe,
#   and likewise for vegetables. 
# - This assumption will often work since a dish typically uses only one type of meat.  
#   But again, this assumption is only being used to provide the user a rough estimate of the 
#   recipe cost.  
# - The main accomplishment of this app, is matching sale items accurately with recipes. 
#   Exact quantities is the next step.
#
# - Normalization is also necessary since for example, one recipe may be proportioned for one 
#   dinner for two, while another might be a whole Thanksgiving turkey designed to serve a party.


# get indices by type (M,P,S) or (F,V) and only those that are priced per lb
# (for items priced per 'ea', we will not normalize to 1 lbs total, but assume
#  user has to buy one of those items (e.g. single serve herb pack))

MPS_ind = np.sort(  np.concatenate((index_M,index_P,index_S)) )   # meat, poultry, seafood
FV_ind  = np.sort(  np.concatenate((index_F,index_V))         )   # fruits, vegetables

recipe_mat_norm = recipe_mat + 0.0

for k in range(n_recipes):
    sum_MPS = np.sum(recipe_mat[k,MPS_ind])
    sum_FV  = np.sum(recipe_mat[k, FV_ind])
    
    if sum_MPS > 0:
        recipe_mat_norm[k,MPS_ind] = recipe_mat[k,MPS_ind]/sum_MPS
        
    if sum_FV > 0:
        recipe_mat_norm[k,FV_ind]  = recipe_mat[k, FV_ind]/sum_FV


# save recipe matrix
np.savez('recipe_matrix.npz', recipe_mat=recipe_mat, recipe_mat_norm=recipe_mat_norm)


