import requests, json, re
from selenium import webdriver
from bs4 import BeautifulSoup

def evine(webpage, upc, upcDir):
	alnumRegex = re.compile("""[^a-zA-Z0-9&"'. ]""")#re.compile('[^a-zA-Z]')
	evineJS = re.compile('clientSideData={.*?};', re.DOTALL)
	print('%s%s' % (webpage, upc))
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
	get = requests.get("%s%s" % (webpage, upc), headers=headers)
	soup = BeautifulSoup(get.content, 'html.parser')
	
	with open('%s/%s-RawHTML.html' % (upcDir, upc), 'wb') as hFile:
		hFile.write(get.content)

	soup = BeautifulSoup(get.content, 'html.parser')

	# Find java script. Parse it for json list of pricing
	images = soup.find_all('product-detail-images-container')
	print(images)
	script = soup.find_all('script')[0].text # get javascript (which has master dictionary) for current product data
	matches = evineJS.search(script) # search page javascript for compiled regex
	matchedJson = matches.group().replace('clientSideData=', '').rstrip(";") # return match and remove excess info to create json format
	productInfo = json.loads(matchedJson) # load matched json format as parseable json object

	productName = productInfo['ProductName']
	productName = re.sub(alnumRegex, ' ', productName).replace('"AS IS"', '').replace('"', '').replace('&', 'and').replace(' w  ', ' w/ ')

	offerCode = productInfo["OfferCode"]
	imageUrl = 'http://s7d1.scene7.com/is/image/ShopHQ/%s' % offerCode
	getImg = requests.get(imageUrl)

	clearancePrice = productInfo["Price"] #main price. Currently being sold at price. Low ball price.
	evinePrice = productInfo["PriceArray"][0]['DisplayPrice']

	customDictionary = {'ProductName': productName,
						'ProductID': upc,
						'AlternateID': offerCode,
						'ClearancePrice': clearancePrice,
						'EvinePrice': evinePrice,
						'ImageLink': imageUrl,
						'ProductUrl': '%s%s' % (webpage, url)
						}

	with open('%s/%s-RawJson.json' % (upcDir, upc), 'w+') as details:# immediately log the product's parseable json info
		json.dump(productInfo, details) # dump to logfile as json
				
	with open('%s/%s-CustomInfo.json' % (upcDir, upc), 'w+') as productTxt:
		json.dump(customDictionary, productTxt)

	with open('%s/%s.jpg' % (upcDir, imageUrl.split('/')[-1]), 'wb') as dlImg: #Download and save main image
		dlImg.write(getImg.content)

	print('%s\n%s\n%s\n' % (productName, imageUrl, [clearancePrice, evinePrice]))#'Clearance: %s\nEvine: %s\n' % (clearancePrice, evinePrice))
	return clearancePrice, evinePrice, imageUrl