import requests, json
from selenium import webdriver
from bs4 import BeautifulSoup

def thd(webpage, upc, upcDir):
		headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
		get = requests.get("%s%s" % (webpage, upc), headers=headers)
		soup = BeautifulSoup(get.content, 'html.parser')

		#function!
		try:
			if soup.find_all("h1", class_="search-tips__heading")[0].text == "Try different search words":
				print("UPC NOT FOUND: %s" % upc)
				return
		except:
			pass

		try:
			mainImg = soup.find_all("div", id="mediaPlayer")[0]
			imgUrl = mainImg.find_all("div", class_="media__main-image")[0].find("img", id="mainImage")["src"]
		except:	
			imgUrl = ""

		try:
			brand = soup.find_all("h2", class_="product-title__brand")[0].find("span", class_="bttn__content").text.strip()
		except:
			brand = ""

		try:
			title = soup.find_all(class_="product-title__title")[0].text.replace("-", " ")
		except:
			title = ""

		try:	
			model = soup.find_all(class_="product_details modelNo")[0].text.strip().replace(" #", ":")
		except:
			model = ""

		try:
			internetNum = soup.find_all("span", itemprop="productID")[0].text.strip()
		except:
			internetNum = ""

		try:	
			storeSku = soup.find_all("span", itemprop="sku")[0].text.strip()
		except:
			storeSku = ""
					
		try:
			price = soup.find_all('span', class_='pReg')[0]["content"]
		except:
			price = ""
					
		try:
			desc = soup.find_all("p", itemprop="description")[0].text.strip()
		except:
			desc = ""

		try:
			bullets = soup.find_all(class_="main_description col-12 col-md-12")[0].find("ul", class_="list")
		except:
			bullets = ""
	
		#function
		finTitle = "%s %s - %s" % (brand, title, model)
		finTitle = finTitle.replace("in.", "inch").replace('"', '').replace("(", "").replace(")", "")

		dimenContent = soup.find_all("div", class_="specs__group col-12 col-lg-6")

		try:
			manuals = soup.find_all("div", id="more-info", class_="info_guides")[0].find("ul", class_="list list--type-plain")
			for a in manuals.find_all("a", href=True):
				hFile = a["href"].split('/')[-1]
				manual = requests.get(a["href"], stream=True)
				with open('%s%s' % (upcDir, hFile), 'wb') as manDoc:
					manDoc.write(manual.content)
				print "Downloaded %s..." % hFile
		except:
			print("This listing doesn't contain 'more-info' docs")

		specs = []
		for each in dimenContent:
			x, y = [each.find("div", class_="col-6 specs__cell specs__cell--label"), each.find("div", class_="col-6 specs__cell")]
			if 'warranty' in x.text.lower() or 'warranty' in y.text.lower():
				pass
			elif 'return' in x.text.lower() or 'return' in y.text.lower():
				pass
			else:
				spec = "<li>%s: %s</li>" % (x.text, y.text)
				specs.append(spec)

		# function
		browser = webdriver.Chrome()
		browser.get("%s%s" % (webpage, upc))
		html = browser.page_source
		soup = BeautifulSoup(html, 'lxml')

		mainImg = soup.find_all("div", class_="media__main-image")
		thumbnails = soup.find_all("div", class_="media__thumbnails")
		imgLinks = [i.find_all('img') for i in thumbnails][0]
		imgJpgs = set([i["src"] for i in imgLinks])

		fullImg = []
		for i in imgJpgs:
			if i.endswith(".jpg"):
				i = i.split("_")[0]
				i += "_1000.jpg"#replace(".jpg", "_500")
				fullImg.append(i)
		browser.close()

		# function - potential repetitive class function
		customDictionary = {'title': title, #array[0]
							'brand': brand, #array[1]
							'model': model, #array[2]
							'internetNo': internetNum, #array[3]
							'storeSku': storeSku, #array[4]
							'retail': price, #array[5]
							'upc': upc, #array[6]
							'description': desc,
							'imgUrl': imgUrl,
							'imgUrls': fullImg,
							'specifications': "".join(set(specs)),
							'productUrl': '%s%s' % (webpage, upc)
							}
							
		with open('%s/%s-CustomInfo.json' % (upcDir, upc), 'w+') as productTxt:
			json.dump(customDictionary, productTxt)
			
		#function	
		try:
			for i, each in enumerate(fullImg):
				getImg = requests.get(each)
				with open('%s/%s__%s.jpg' % (upcDir, each.split('/')[-1].replace(".jpg", ""), i), 'wb') as dlImg: #Download and save main image
					dlImg.write(getImg.content)
				print 'Downloaded picture #%s' % i
		except:
			pass