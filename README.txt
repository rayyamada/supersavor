
------------------------------------------------------------------------
------------------------------------------------------------------------
I. INTRODUCTION

The supersavor app is a collection of python scripts which
1) run a web app via Dash
2) scrape online websites for sales  
3) finds recipes in a recipe database that optimally utilize the sales.

The web app allows the user to select preferences (e.g. meat, no meat, budget, etc...)
and recommends recipes in order of those that save the most money.  The app is meant to facilitate the process of having to look through sales and choose recipes, thereby saving the user time and money. 

The web app is hosted on AWS at http://www.supersavorapp.website/
The recipe database can be found at https://www.kaggle.com/hugodarwood/epirecipes#full_format_recipes.json

------------------------------------------------------------------------
------------------------------------------------------------------------
II. OVERVIEW OF SCRIPTS

The scripts currently consist of around 2000 lines of python code and have the following components:


scripts 1-4 are preliminary scripts (i.e., need to be run only once and/or infrequently updated)

1. savor_nouns.py   (only needs to be run once)

- this script generates a list of the most popular unigram nouns (ingredients, like 'tomato','chicken',...) from the recipe database. 
- saves a file  'nouns.csv'
- since our dataset of ingredients is unlabeled (we are learning them through unsupervised 
learning


2. savor_ingred_list.py  (only needs to be run once; must be run after 1.)

- this script takes nouns in 'nouns.csv' and generates the list of ingredients, which includes the most common bi- and tri-grams  (e.g. 'cherry tomato')
- saves a file 'ingredients_list.csv' and an abbreviated list 'ingredients_list_short.csv'
The latter removes some non-food words from the list (e.g. 'thermometer')
 

3. savor_base_prices.py  (only run occasionally (e.g. seasonally) to update non-sale prices; must be run after 2.)

- using the online non-sale prices for all goods, tries to find a price for every item
in our 'ingredients_list_short.csv' from step 2.
- saves the price, item name, sku, units of the ingredients in  'base_price_vec.csv'
- the output 'base_price_vec.csv' is provided


4. savor_recipemat.py  (only needs to be run once, after 2.  Update as needed if 
recipe database or ingredients list changes)

- codifies in a matrix which ingredients are used in a recipe.  The rows of the matrix are recipes and the columns are ingredients from ingredients_list_short.csv
- the recipe matrix is saved to a file 'recipe_matrix.npz'

	     --------------------------------------------

5. app.py
- main script that runs the web app in Dash
- creates the GUI interface in html 
- scrapes online sales data as needed (FD_scrape.py)
- finds recipes that maximize savings based on sales data and user preferences (savor.py)


6. FD_scrape.py
- scrape sales pages from FreshDirect.com
- is set to scrape at most once a day
- scraping can be disabled altogether by setting 'autoscrape = False' in app.py


7. savor.py
- contains the main codes for finding optimal recipes based on sales
- also contains utility functions, such as for cleaning text

------------------------------------------------------------------------
------------------------------------------------------------------------


 
