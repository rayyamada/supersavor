# script to scrape sales pages from FreshDirect.com
from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import re
from time import sleep, time
from os.path import getmtime

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
def scrape_sales():
	
	# - only scrape sales if they haven't already been checked within the last 24 hrs
	current_time = time()
	secinday = 24*60*60


	#  VEGETABLES and FRUITS SALES PAGE

	my_urls = ['https://www.freshdirect.com/browse.jsp?pageType=browse&id=veg_sale&pageSize=30&all=true&activePage=0&sortBy=Sort_SaleUp&orderAsc=true&activeTab=product&pfg_orgnat_veg=clearall',
			   'https://www.freshdirect.com/browse.jsp?pageType=browse&id=fru_sale&pageSize=30&all=true&activePage=0&sortBy=Sort_SaleUp&orderAsc=true&activeTab=product&pfg_orgnat_fruit=clearall'
			   ]

	filenames = ['vegetables.csv','fruits.csv'] 


	for ii in range(len(my_urls)):
		my_url = my_urls[ii]
		filename = filenames[ii]

		# check timestamp
		if (current_time - getmtime(filename)) < secinday:
			continue


		req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
		uClient = urlopen(req)       # open connection, grab page
		page_html = uClient.read()    
		uClient.close()              # close connection

		page_soup = soup(page_html, 'html.parser')    # html parsing

		# grab each listed item
		items = page_soup.findAll('li',{'class':'portrait-item'})

		f = open(filename, 'w')

		headers = 'item_name,sku_code,orig_price,sale_price,sale_pct,in_stock,freshness_rating,units_soldas,units_descr\n'

		f.write(headers)


		# loop through all sale items and save to csv
		for item in items:
		    
		    in_stock = bool( item["data-in-stock"] )       # should be true
		    

		    #data_price = float(item["data-price"])      # price including sale, but does not include maximum sale if say 4 for 1
		                             # for our first pass, we will use maximum sale price, computing by 
		                             # taking percent savings from original price

		    #print('data price: ' + str(data_price) )

		    temp = item.findAll('div',{'class':'cssBurst deal'})
		    if len(temp) > 0:  # --ERROR HANDLING-- # this ensures item is on sale (otherwise this would be missing)
		        sale_pct = 0.01*float(temp[0].text[4:].strip('%'))        # sale percentage

		        temp = item.findAll('div',{'class':'portrait-item-price'})
		        match = re.search('^.\d+.\d+', temp[0].text.strip())   # sometimes the price with
		        orig_price = float(match.group().strip('$'))           # the strikethrough is missing
		        sale_price = round( (1-sale_pct)*orig_price, 2)    
		            
		        try:  # --ERROR HANDLING--
		            temp2 = float(temp[0].s.text.strip().strip('$'))
		            orig_price = temp2
		            sale_price = round( (1-sale_pct)*orig_price, 2)
		        except:
		        #    continue  # if price is not available (or not formatted righ), then skip
		            #orig_price = ''
		            #sale_price = ''
		            foo31 = 2
		            
		            
		        # units_soldas
		        temp3 = re.search('\/[a-z]+', temp[0].text.strip() )
		        if not temp3 is None:
		            units_soldas = temp3.group()[1:]
		        else:
		            units_soldas = ''
		            
		        # units_descr
		        temp = item.findAll('div',{'class':'configDescr'})
		        if len(temp) == 0:
		            units_descr = ''
		        else:
		            units_descr = temp[0].text.replace(',','')
		            

		        # item name 
		        temp = item.findAll('span',{'class':'portrait-item-header-name'})
		        temp = temp[0]   # the second one is for pop-up suggestions which we don't care about

		        item_name = temp.text.replace(',','')       # scraping "product item header name"
		                                             # replace comma with blank, or it messes up csv
		        
		        
		        # freshness rating
		        temp = item.findAll('div',{'class':'rating'})
		        temp = temp[0].text
		        if len(temp) > 0 and temp != 'Not rated':    # --ERROR HANDLING--
		            temp2 = re.search('\d.?\d?',temp)
		            freshness_rating = temp2.group()   # *** TO DO ***  need to modify for those with half ratings, like 3.5 out of 5
		        else:
		            freshness_rating = ''

		            
		        # sku code
		        temp = item.findAll('input', {'data-component':'productData'})
		        for i in range(len(temp)):
		            if temp[i]['data-productdata-name'] == 'skuCode':
		                sku_code = temp[i]['value']
		                break

		                
		        # write item entry to csv file
		        f.write(item_name + ',' + \
		                sku_code + ',' + \
		                "{:.2f}".format(orig_price) + ',' + \
		                "{:.2f}".format(sale_price) + ',' + \
		                str(round(sale_pct,2)) + ',' + \
		                str(in_stock) + ',' + \
		                freshness_rating + ',' + \
		                units_soldas + ',' + \
		                units_descr  + '\n'
		               )

		f.close()
		print('wrote '+ filename)
		sleep(1)


	 
	# MEAT, POULTRY, and SEAFOOD  SALES PAGE   (parsing slightly different)
	my_urls = ['https://www.freshdirect.com/browse.jsp?pageType=browse&id=mea_sale_valpack&pageSize=30&all=true&activePage=0&sortBy=Sort_SaleUp&orderAsc=true&activeTab=product&pfg_cos_meat=clearall',
			   'https://www.freshdirect.com/browse.jsp?pageType=browse&id=pou_sale&pageSize=30&all=true&activePage=1&sortBy=Sort_SaleUp&orderAsc=true&activeTab=product',
			   'https://www.freshdirect.com/browse.jsp?pageType=browse&id=sea_sale&pageSize=30&all=false&activePage=1&sortBy=Sort_SaleUp&orderAsc=true&activeTab=product'
			   ]

	filenames = ['meat.csv','poultry.csv','seafood.csv'] 


	for ii in range(len(my_urls)):
		my_url = my_urls[ii]
		filename = filenames[ii]

		# check timestamp
		if (current_time - getmtime(filename)) < secinday:
			continue

		req = Request(my_url, headers={'User-Agent': 'Mozilla/5.0'})
		uClient = urlopen(req)       # open connection, grab page
		page_html = uClient.read()    
		uClient.close()              # close connection

		page_soup = soup(page_html, 'html.parser')    # html parsing


		# grab each listed item
		items = page_soup.findAll('li',{'class':'portrait-item'})

		f = open(filename, 'w')

		headers = 'item_name,sku_code,orig_price,sale_price,sale_pct,in_stock,freshness_rating,units_soldas,units_descr\n'

		f.write(headers)


		# loop through all sale items and save to csv
		for item in items:
		    
		    in_stock = bool( item["data-in-stock"] )       # should be true
		    

		    temp = item.findAll('div',{'class':'cssBurst deal'})
		    
		    
		    if len(temp) > 0:  # --ERROR HANDLING-- # this ensures item is on sale (otherwise this would be missing)
		        # if the item is not on sale, then this item will be skipped
		        sale_pct = round(0.01*float(temp[0].text[4:].strip('%')),2)        # sale percentage

		        temp = item.findAll('div',{'class':'portrait-item-price'})
		        #match = re.search('^.\d+.\d+', temp[0].text.strip())   # sometimes the price with
		        #orig_price = float(match.group().strip('$'))           # the strikethrough is missing
		        #sale_price = round( (1-sale_pct)*orig_price, 2)    
		            
		        try:  # --ERROR HANDLING--
		            temp2 = float(temp[0].s.text.strip().strip('$'))
		            orig_price = temp2
		            
		            temp3 = item.findAll('span',{'class':'save-price'})
		            sale_price = re.search('^\$\d+\.\d+', temp3[0].text.strip() ).group().strip('$')
		            
		            # sale_price = round( (1-sale_pct)*orig_price, 2)
		        except:
		        #    continue  # if price is not available (or not formatted righ), then skip
		            orig_price = ''
		            sale_price = ''
		            foo31 = 2
		            
		            
		        # units_soldas
		        temp3 = re.search('\/[a-z]+', temp[0].text.strip() )
		        if not temp3 is None:
		            units_soldas = temp3.group()[1:]
		        else:
		            units_soldas = ''
		            
		        # units_descr
		        temp = item.findAll('div',{'class':'configDescr'})
		        if len(temp) == 0:
		            units_descr = ''
		        else:
		            units_descr = temp[0].text.replace(',','')
		            

		        # item name 
		        temp = item.findAll('span',{'class':'portrait-item-header-name'})
		        temp = temp[0]   # the second one is for pop-up suggestions which we don't care about

		        item_name = temp.text.replace(',','')       # scraping "product item header name"
		                                             # replace comma with blank, or it messes up csv
		        

		        
		        # freshness rating
		        temp = item.findAll('div',{'class':'rating'})
		        temp = temp[0].text
		        if len(temp) > 0 and temp != 'Not rated':    # --ERROR HANDLING--
		            temp2 = re.search('\d.?\d?',temp)
		            freshness_rating = temp2.group()   # *** TO DO ***  need to modify for those with half ratings, like 3.5 out of 5
		        else:
		            freshness_rating = ''

		            
		        # sku code
		        temp = item.findAll('input', {'data-component':'productData'})
		        for i in range(len(temp)):
		            if temp[i]['data-productdata-name'] == 'skuCode':
		                sku_code = temp[i]['value']
		                break

		                
		        # write item entry to csv file
		        f.write(item_name + ',' + \
		                sku_code + ',' + \
		                "{:.2f}".format(orig_price) + ',' + \
		                sale_price + ',' + \
		                str(sale_pct) + ',' + \
		                str(in_stock) + ',' + \
		                freshness_rating + ',' + \
		                units_soldas + ',' + \
		                units_descr  + '\n'
		               )

		f.close()
		print('wrote '+ filename)
		sleep(1)

	return

#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

