import numpy as np
import pandas as pd
import re
#import matplotlib.pyplot as plt

#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from nltk import ngrams




#-----------------------------------------------------------------
# FUNCTION DEFINITIONS
#-----------------------------------------------------------------
def clean_item_text(item_text):
    # process a line of text describing an ingredient
    #  - remove endings like 's' and 'es'  and convert 'ies' to 'y'
    #
    # CountVectorizer removes the hyphens between words  things like '1/2' also disappear
    #   note:  CountVectorizer makes everything lower case

    item_list = item_text.split()

    # process text
    item_list = [re.sub(',$','',word) for word in item_list]       # remove commas
    item_list = [re.sub('\(|\)','',word) for word in item_list]    # remove parentheses
    item_list = [re.sub('-',' ',word) for word in item_list]       # replace - with space

    item_list = [re.sub('ies$','y',word) for word in item_list] 
    item_list = [re.sub('s$|es$','',word) for word in item_list]   #  'slices' to 'slic'
    
    item_list = [re.sub('\d+\/\d+','',word) for word in item_list]  # remove fractions
    item_list = [re.sub('^\d+','',word) for word in item_list]      # remove numbers
        
    
    # remove stop words   
    stopwords = ['cup','cups', 'teaspoon','teaspoons','tablespoon','tablespoons',
                 'pound','pounds','lb','lbs', 
                 'ounc', 'ounce', 'ounces', 'oz',  'tsp', 'tbsp', 'ml', 'qt', 'quart',
                 'pint', 'pints', 'bunch', 'stick', 'sticks', 
                 'inch', 'head', 'sprig', 
                 'pinch', 'piece', 'piec' ]   # + list(ENGLISH_STOP_WORDS)
                                              # 'whole' is a stop word

    item_list  = [word for word in item_list if word.lower() not in stopwords]
    item_str =  ' '.join(item_list)

    return item_str

# ------------------------------------------------------------

remove_words = ['kit', 'farm share', 'case', 'medley','noodles'] 

def get_removelist(dataframe):
	# - remove sales item names from dataframe that contain any 
	#   words in remove_words list
	temp = []
	for i in range(dataframe.shape[0]):
		name_words = dataframe.item_name[i].lower()

		for word in remove_words:
			if re.search(word, name_words):
				temp.append(i)


	#for i in range(dataframe.shape[0]):
	#    name_words = dataframe.item_name[i].lower().split()
	#    for word in remove_words:
	#        if word in name_words:
	#            temp.append(i)

	return temp

# ------------------------------------------------------------

def normalize_prices(dataframe):
# - normalize price of ingredients to 'per lb'
# - will convert oz to lb
# 	- change units to lbs only if it's greater than 3/16 lbs (see below)
# - converts #packs of n#  to price for one item

	for i_ in range(len(dataframe)):
	    i = dataframe.index[i_]

	    if dataframe.loc[i,'units_soldas'] == 'ea':       # units_soldas is ea
	        
	        if not dataframe.units_descr.isna().loc[i]:   # units_descr can't be missing (nan)
	            
	            # look for descriptions in lbs
	            test = re.search('\d+lb|\d+\.\d+lb', dataframe.loc[i,'units_descr'])
	            if not test is None:
	                wgt_lb = float(re.sub('lb','',test[0]))  # get weight in lbs
	                
	                dataframe.loc[i,'units_soldas'] = 'lb'
	                dataframe.loc[i,'units_descr'] = ''
	                dataframe.loc[i,'orig_price'] = round(dataframe.loc[i,'orig_price']/wgt_lb,2)
	                dataframe.loc[i,'sale_price'] = round(dataframe.loc[i,'sale_price']/wgt_lb,2)
	                
	            # look for descriptions in oz
	            test = re.search('\d+oz|\d+\.\d+oz',dataframe.loc[i,'units_descr'])
	            if not test is None:
	                wgt_lb = float(re.sub('oz','',test[0]))/16  # get weight in lbs (1lb=16oz)
	                
	                # change units to lbs only if it's greater than 3/16 lbs
	                # - some small items, like a single pack of herbs weigh very little, 
	                #   a recipe would require just one pack and weight by pounds is not 
	                #   the best way to measure.
	                if wgt_lb > 2.9/16:
	                    dataframe.loc[i,'units_soldas'] = 'lb'
	                    dataframe.loc[i,'units_descr'] = ''
	                    dataframe.loc[i,'orig_price'] = round(dataframe.loc[i,'orig_price']/wgt_lb,2)
	                    dataframe.loc[i,'sale_price'] = round(dataframe.loc[i,'sale_price']/wgt_lb,2)
	                
	            # look for descriptions in ct,pk (where "ea" is one pack)
	            test = re.search('\d+pk|\d+ct',dataframe.loc[i,'units_descr'])
	            if not test is None:
	                ct_ = float(re.sub('ct|pk','',test[0]))
	                dataframe.loc[i,'units_descr'] = ''
	                dataframe.loc[i,'orig_price'] = round(dataframe.loc[i,'orig_price']/ct_,2)
	                dataframe.loc[i,'sale_price'] = round(dataframe.loc[i,'sale_price']/ct_,2)
	            
	    # else if ... == 'lb'    # do nothing

	return
    

# ------------------------------------------------------------

# ------------------------------------------------------------


# ------------------------------------------------------------


# ------------------------------------------------------------
#-----------------------------------------------------------------



#-----------------------------------------------------------------
#-----------------------------------------------------------------
def initialize():

	# read recipe database json file
	df_epi = pd.read_json('epicurious-recipes-with-rating-and-nutrition/full_format_recipes.json')

	df_epi = df_epi.loc[:,['ingredients','title','directions']]


	df2 = df_epi.iloc[0:5000,:]    # FIRST, try use ONLY FIRST  N recipes


	# clean recipe data - missing ingredients list
	temp = []
	for i in range(df2.shape[0]):
	    if type(df2.ingredients[i]) != list:
	        temp.append(i)
	        
	        
	df2 = df2.drop(temp)  
	n_recipes = df2.shape[0]


	# ------------------------------------------------------------
	# READ in  "list of ingredients"
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


	# ------------------------------------------------------------
	# READ in  "sales page"
	poultry = pd.read_csv('poultry.csv')
	meat = pd.read_csv('meat.csv')
	vegetables = pd.read_csv('vegetables.csv')
	fruits = pd.read_csv('fruits.csv')
	seafood = pd.read_csv('seafood.csv')


	# ------------------------------------------------------------
	# REMOVE ITEMS with words from remove_words list
	# remove_words - if these words are present in the item name, then remove item
	 
	temp = get_removelist(vegetables)        
	vegetables = vegetables.drop(temp)  

	temp = get_removelist(fruits)
	fruits = fruits.drop(temp)

	temp = get_removelist(poultry)
	poultry = poultry.drop(temp)  

	temp = get_removelist(meat)
	meat = meat.drop(temp)  

	temp = get_removelist(seafood)  
	seafood = seafood.drop(temp)  


	# NORMALIZE PRICES
	normalize_prices(vegetables)
	normalize_prices(fruits)
	normalize_prices(poultry)
	normalize_prices(meat)
	normalize_prices(seafood)


	# ------------------------------------------------------------
	# SALES VECTOR ENCODER  V2
	#
	# -create a sales dataframe (sales_df) with the number of rows equal to n_items 
	# (length of our "list of ingredients")
	# -for each item, we will try to find a sale item that fits that item type
	#
	# algorithmically, 
	# - for each sale item, search if it is in "list of ingredients."  If a sale item has the word
	#   "beef flank steak" in it, first try to match it with trigrams and then bigrams.  If the
	#   list of ingredients has "beef flank steak" and "flank steak", both will be matched, i.e. 
	#   this sale item can work for any recipe containing either one of those phrases. 
	#     If no bigrams or trigrams are matched, then we will match unigrams, which will be used 
	#     for vauge recipes that, for example, only specify "beef" or "steak".
	#
	# - if a sale items falls into a category that already has a sale item logged, replace it
	#   only if this item is "better"  (sale item has better savings than previous)
	#
	#  sales_vec - pandas dataframe with rows corresponding to ingred_list
	#    columns:   item_name, sku_code, orig_price, sale_price, savings (orig_price-sale_price)
	#
	#  sales_df  - pandas dataframe containing list of all sale items
	#    columns:   item_name, sku_code, orig_price, sale_price, savings (orig_price-sale_price)
	#

	sales_list = list(vegetables.item_name.values) + list(poultry.item_name.values) + \
	             list(meat.item_name.values) + list(fruits.item_name.values) + \
	             list(seafood.item_name.values)

	sku_list = list(vegetables.sku_code.values) + list(poultry.sku_code.values) + \
	           list(meat.sku_code.values) + list(fruits.sku_code.values) + \
	           list(seafood.sku_code.values)

	origpr_list = list(vegetables.orig_price.values) + list(poultry.orig_price.values) + \
	              list(meat.orig_price.values) + list(fruits.orig_price.values) + \
	              list(seafood.orig_price.values)

	salepr_list = list(vegetables.sale_price.values) + list(poultry.sale_price.values) + \
	              list(meat.sale_price.values) + list(fruits.sale_price.values) + \
	              list(seafood.sale_price.values)


	sales_df = pd.DataFrame({ 'item_name'  : sales_list,
	                          'sku_code'   : sku_list,
	                          'orig_price' : origpr_list,
	                          'sale_price' : salepr_list,
	                          'savings'    : list(np.round(np.array(origpr_list)-np.array(salepr_list),2))
	                        } )

	n_sales = sales_df.shape[0]


	sales_vec = pd.DataFrame({ 'item_name'  : '',
	                          'sku_code'   : '',
	                          'orig_price' : np.zeros(n_items),
	                          'sale_price' : np.zeros(n_items),
	                          'savings'    : np.zeros(n_items)
	                        } )

	bool_vec  = np.zeros(n_items, dtype=bool)   # bool_vec is used to specify if a sale item has
	                                            # been found for a particular ingred_list item

	#-------------    
	    
	# encode sale items' prices into sales_df

	for i in range(n_sales):    # for each sale item
	    name = sales_df.item_name[i].lower()
	    
	    sale_found = False     # boolean flag if ingred match is found for this sale item
	    
	    # from sale item name create unigram,bigram,trigram lists
	    unigram_list = clean_item_text(name).split() # clean list
	    
	    temp = list(ngrams( unigram_list, 2 ))
	    bigram_list = [' '.join(tup) for tup in temp]
	    
	    temp = list(ngrams( unigram_list, 3 ))
	    trigram_list = [' '.join(tup) for tup in temp]
	    
	    
	    # does sale item name match any n-grams in ingred_list  ?    
	    for k in range(n_items):  # for each item in ingred_list
	        
	        if ingred_list[k] in (bigram_list + trigram_list):  # any matching 2,3-grams?
	            
	            sale_found = True
	            
	            # check if another sale item has already been found
	            #  -if no, move sale item data into sales_vec dataframe
	            #  -if yes, compare which sale is better and possibly replace
	            if bool_vec[k] == False:  # no sale item has been found for this ingred yet
	                sales_vec.loc[k,'item_name']  = sales_df.item_name[i]
	                sales_vec.loc[k,'sku_code']   = sales_df.sku_code[i]
	                sales_vec.loc[k,'orig_price'] = sales_df.orig_price[i]
	                sales_vec.loc[k,'sale_price'] = sales_df.sale_price[i]
	                sales_vec.loc[k,'savings']    = sales_df.savings[i]
	                bool_vec[k] = True
	            else: # compare with existing
	                 if sales_df.savings[i] > sales_vec.savings[k]:  # better deal, replace item
	                        sales_vec.loc[k,'item_name']  = sales_df.item_name[i]
	                        sales_vec.loc[k,'sku_code']   = sales_df.sku_code[i]
	                        sales_vec.loc[k,'orig_price'] = sales_df.orig_price[i]
	                        sales_vec.loc[k,'sale_price'] = sales_df.sale_price[i]
	                        sales_vec.loc[k,'savings']    = sales_df.savings[i]                    
	        
	        
	    if sale_found == False:
	        # since we're looping with ingred_list rather than from the n-gram list, we have
	        # to first search through the entire ingred_list for 2,3 grams before searching 
	        # unigram matches.  Hence we have another 'for k in range(n_items)'' loop here.
	        # Otherwise, e.g., if 'potato' is in ingred_list and 'sweet potato'
	        # is on sale, then after failing to match 'potato' to any 2,3-grams it would match
	        # to the unigram 'potato' in 'sweet potato', which would then recommend sweet potatoes
	        # for recipes that used just 'potato'
	        
	        for k in range(n_items):  # for each item in ingred_list
	            if ingred_list[k] in unigram_list: 
	                # the sale item name only matches unigrams (no bi,trigram matches found) 
	                if bool_vec[k] == False:  # no sale item has been found for this ingred yet
	                    sales_vec.loc[k,'item_name']  = sales_df.item_name[i]
	                    sales_vec.loc[k,'sku_code']   = sales_df.sku_code[i]
	                    sales_vec.loc[k,'orig_price'] = sales_df.orig_price[i]
	                    sales_vec.loc[k,'sale_price'] = sales_df.sale_price[i]
	                    sales_vec.loc[k,'savings']    = sales_df.savings[i]
	                    bool_vec[k] = True
	                else: # compare with existing
	                     if sales_df.savings[i] > sales_vec.savings[k]:  # better deal, replace item
	                            sales_vec.loc[k,'item_name']  = sales_df.item_name[i]
	                            sales_vec.loc[k,'sku_code']   = sales_df.sku_code[i]
	                            sales_vec.loc[k,'orig_price'] = sales_df.orig_price[i]
	                            sales_vec.loc[k,'sale_price'] = sales_df.sale_price[i]
	                            sales_vec.loc[k,'savings']    = sales_df.savings[i]  


	        
	#---------------------------------
	# LOAD RECIPE MATRIX
	
	data_rm = np.load('recipe_matrix.npz')
	recipe_mat = data_rm['recipe_mat']
	recipe_mat_norm = data_rm['recipe_mat_norm']

	# LOAD base_prices
	base_vec = pd.read_csv('base_price_vec.csv')
	orig_prices = base_vec.orig_price.values
	#unit_labels = base_vec.units_soldas.values


	return df2, ingred_list, main_list, bool_vec, sales_vec, \
		   recipe_mat,recipe_mat_norm, orig_prices

#-----------------------------------------------------------------
#-----------------------------------------------------------------

#-----------------------------------------------------------------
#-----------------------------------------------------------------
def update(df2, ingred_list, main_list, bool_vec, sales_vec, \
		   recipe_mat,recipe_mat_norm, orig_prices, \
		   checkbox_values,slider_values):

	#print('savor.update:')
	#print(checkbox_values)
	#print(slider_values)

	#---------------------------------
	# GET recipe indices by which we can filter out recipes containing  F,V,M,P,S 

	index_F = np.nonzero(main_list.type=='F')[0]    # F-ruits
	index_V = np.nonzero(main_list.type=='V')[0]    # V-egetables
	index_M = np.nonzero(main_list.type=='M')[0]    # M-eats
	index_P = np.nonzero(main_list.type=='P')[0]    # P-oultry
	index_S = np.nonzero(main_list.type=='S')[0]    # S-eafood
	#index_D = np.nonzero(main_list.type=='D')[0]    # D-airy

	# find recipe indices that contain no F,V,M,P,S,D
	ind_noF = (np.sum(recipe_mat[:,index_F], axis=1) == 0) 
	ind_noV = (np.sum(recipe_mat[:,index_V], axis=1) == 0) 
	ind_noM = (np.sum(recipe_mat[:,index_M], axis=1) == 0)
	ind_noP = (np.sum(recipe_mat[:,index_P], axis=1) == 0)
	ind_noS = (np.sum(recipe_mat[:,index_S], axis=1) == 0) 
	#ind_noD = (np.sum(recipe_mat[:,index_D], axis=1) == 0) 


	#---------------------------------
	# FIND OPTIMAL RECIPES

	# filters
	if 'F' in checkbox_values:
		filt_F = False
	else:
		filt_F = True

	if 'V' in checkbox_values:
		filt_V = False
	else:
		filt_V = True

	if 'M' in checkbox_values:
		filt_M = False
	else:
		filt_M = True

	if 'P' in checkbox_values:
		filt_P = False
	else:
		filt_P = True

	if 'S' in checkbox_values:
		filt_S = False
	else:
		filt_S = True

	#filt_F = False
	#filt_V = False
	#filt_M = False
	#filt_P = False
	#filt_S = False
	#filt_D = False

	filt_ind = np.ones(recipe_mat.shape[0],dtype=bool)
	orig_index = np.arange(0,recipe_mat.shape[0])

	if filt_F:
	    filt_ind = filt_ind*ind_noF
	if filt_V:
	    filt_ind = filt_ind*ind_noV
	if filt_M:
	    filt_ind = filt_ind*ind_noM
	if filt_P:
	    filt_ind = filt_ind*ind_noP
	if filt_S:
	    filt_ind = filt_ind*ind_noS
	#if filt_D:
	#    filt_ind = filt_ind*ind_noD
	    

	# filter out recipes in which an M,P,S was found in ingred_list, but not on FreshDirect.
	# -in this case, this is a bad recipe because the user cannot purchase the ingredients 
	#  (probably main ingredient) from the website.  Also, messes up recipe cost estimate
	#  significantly.  
	# - Require that a recipe which has M,P,S flagged has at least one matching MPS on website.

	ind_match = np.ones(recipe_mat.shape[0],dtype=bool)
	bool_MPS = ((main_list.type=='P')|(main_list.type=='M')|(main_list.type=='S'))
	for j in range(recipe_mat.shape[0]):
	    # find ingreds which are in recipe j and contain either P,M, or S
	    temp_ind =  bool_MPS & (recipe_mat[j,:]>0)  
	    
	    # if recipe j contains either P,M, or S  BUT  no matching item(s) found on sales page
	    if (np.sum(temp_ind) > 0) and (len(np.nonzero(orig_prices[temp_ind])[0])==0):
	        ind_match[j] = False

	        
	        
	filt_ind = filt_ind*ind_match
	    
	new_index = orig_index[filt_ind]

	    
	savings_vector = sales_vec.savings.values

	saleprices = sales_vec.sale_price.values
	origprices = sales_vec.orig_price.values
	saleprices[saleprices==0] = orig_prices[saleprices==0]
	origprices[origprices==0] = orig_prices[origprices==0]


	#recipe_mat_filt = recipe_mat[filt_ind,:]
	recipe_mat_filt = recipe_mat_norm[filt_ind,:]  # use normalized recipe matrix

	total_savings = np.matmul(recipe_mat_filt, savings_vector)
	price_sale    = np.matmul(recipe_mat_filt, saleprices)
	price_orig    = np.matmul(recipe_mat_filt, origprices)


	argsort_savings = np.argsort(total_savings)
	argsort_savings = argsort_savings[::-1]
	max_savings     = total_savings[argsort_savings]
	totalcost_sale  = price_sale[argsort_savings]
	totalcost_orig  = price_orig[argsort_savings]



	nshow = 30   # number of recipes to show
	inds = []

	if slider_values[1] == 50:  # maximum selectable value
		slider_values[1] = np.inf

	for i in range(len(totalcost_sale)):
	    if (totalcost_sale[i] >= slider_values[0]) and (totalcost_sale[i] <= slider_values[1]):
	        inds.append(i)


	
	if len(inds) == 0:
		recipe_title = ['(no recipes found)','','','','',
		 								  '','','','','']
		recipe_ingredients = ['','','','','','','','','','']
		recipe_directions = ['','','','','','','','','','']
		sale_ingredients = ['','','','','','','','','','']
		other_ingredients = ['','','','','','','','','','']
		sale_prices = ['','','','','','','','','','']
		sale_titles = ['','','','','','','','','','']
		savings_amounts = ['','','','','','','','','','']
		savings_percent = ['','','','','','','','','','']
		orig_cost   = ['','','','','','','','','','']
		sale_cost   = ['','','','','','','','','','']

		return recipe_title, recipe_ingredients, recipe_directions, \
			   sale_ingredients, other_ingredients, sale_prices, \
			   sale_titles, savings_amounts, savings_percent, \
			   orig_cost, sale_cost

	else:
		i_ = df2.index[ new_index[argsort_savings] ][inds[0:max(nshow,len(inds))]]         # use i_ to correctly index dataframe
	
		ind_ = 0
		ind = inds[ind_]

		i_ind = i_[ind_]

		recipe_title        = list(df2.title[i_].values)
		recipe_ingredients  = df2.ingredients[i_].values
		recipe_directions   = df2.directions[i_].values

		sale_ingredients = []
		other_ingredients = []
		sale_prices = []

		sale_titles = []
		savings_amounts = []
		savings_percent = []

		sale_cost = []
		orig_cost = []

		for i in range(nshow):

			if i < len(inds):
				ii = inds[i]
				sale_ingredients.append(
					list( np.array(ingred_list)[ (recipe_mat_filt[argsort_savings[ii],:]>0) * bool_vec ]  )
			        )
				other_ingredients.append(
			    	list( np.array(ingred_list)[ (recipe_mat_filt[argsort_savings[ii],:]>0) & (origprices>0) ] )
			    	)
				sale_prices.append(
					list( np.round(saleprices[ (recipe_mat_filt[argsort_savings[ii],:]>0) & (origprices>0) ] * \
						recipe_mat_filt[argsort_savings[ii], 
						(recipe_mat_filt[argsort_savings[ii],:]>0) & (origprices>0) ],2 ) )
					)
				sale_titles.append(
					list( sales_vec.item_name.values[ (recipe_mat_filt[argsort_savings[ii],:]>0) * bool_vec ] )
					)
				savings_amounts.append(
					list( savings_vector[ (recipe_mat_filt[argsort_savings[ii],:]>0) * bool_vec ] )
					)
				savings_percent.append( 
					str(int( 100*(totalcost_orig[ii]-totalcost_sale[ii])/totalcost_orig[ii]))
			        )
				sale_cost.append(  str(round(totalcost_sale[ii],2)) )
				orig_cost.append(  str(round(totalcost_orig[ii],2)) )
			else:
				sale_ingredients.append( [] )
				other_ingredients.append( [] )
				sale_prices.append( [] )
				sale_titles.append( [] )	
				savings_amounts.append( [] )
				savings_percent.append( '' )
				sale_cost.append( '' )
				orig_cost.append( '' )

				recipe_title.append( '' )





		return recipe_title, recipe_ingredients, recipe_directions, \
			   sale_ingredients, other_ingredients, sale_prices, \
			   sale_titles, savings_amounts, savings_percent, \
			   orig_cost, sale_cost

	# savings_vector = sales_vec.savings.values

	# temp = np.matmul(recipe_mat,savings_vector)

	# max_savings    = np.max(temp)
	# argmax_savings = np.argmax(temp)

	# i_ = df2.index[argmax_savings]         # use i_ to correctly index dataframe
	# recipe_title       = df2.title[i_]         # str
	# recipe_ingredients = df2.ingredients[i_]   # list
	# recipe_directions  = df2.directions[i_]    # list


	# # recipe_mat[argmax_savings,:] * bool_vec   =  sale items in recipe of max savings
	# sale_ingredients = list(  np.array(ingred_list)[ (recipe_mat[argmax_savings,:]>0) * bool_vec ]  )
	# sale_titles = list( sales_vec.item_name.values[ (recipe_mat[argmax_savings,:]>0) * bool_vec ] )
	# savings_amounts = list( savings_vector[ (recipe_mat[argmax_savings,:]>0) * bool_vec ] )



#	return recipe_title, recipe_ingredients, recipe_directions, \
#		   sale_ingredients, sale_titles, savings_amounts 

	# ingred_list - is a list containing the "list of ingredients" after processing text 
	#				(e.g. removing 's','es', etc...)
	# main_list   - is a pandas dataframe containing the "list of ingredients" before text
	#               processing
	#
	# (sales_df)  - dataframe containing item_name, sku_code, orig_price, sale_price, savings
	# 				for all sale items in the list 'sales_list'
	#				Has n_sales # of rows,  where n_sales is the number of sale items online.
	# sales_vec   - dataframe containing item_name, sku_code, orig_price, sale_price, savings
	# 				for all items in ingred_list for which matching sale items could be found.
	#				Naturally, many rows (corresponding to a non-sale item) will be blank.
	#				(Use sales_vec[bool_vec]  to display info for only those ingreds for which 
	#				sale items were found.)
	#				Has n_items # of rows, where n_items is the length of ingred_list
	# bool_vec    - boolean array specifying whether a sale item for an item in
	#				ingred_list has been found.  Has length n_items.			


#-----------------------------------------------------------------
#-----------------------------------------------------------------


