import requests, json
from selenium import webdriver
from bs4 import BeautifulSoup

def qvc(webpage, upc, upcDir):	
	print('%s%s' % (webpage, upc))
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}
	get = requests.get("%s%s" % (webpage, upc), headers=headers)
	soup = BeautifulSoup(get.content, 'html.parser')
		
	scriptProduct = soup.find_all('script', id='productJSON')[0].text
	scriptMedia = soup.find_all('script', id="mediaJSON")[0].text#[0].text

	scriptProductJSON = json.loads(scriptProduct.encode("utf-8"))
	scriptMediaJSON = json.loads(scriptMedia.encode("utf-8"))

	with open('%s/%s-mediaJson.json' % (upcDir, upc), 'w+') as details:# immediately log the product's parseable json info
		json.dump(scriptMediaJSON, details) # dump to logfile as json

	with open('%s/%s-productJson.json' % (upcDir, upc), 'w+') as details:# immediately log the product's parseable json info
		json.dump(scriptProductJSON, details) # dump to logfile as json

	#print(scriptMediaJSON["image"])
	for key in scriptMediaJSON:
		val = scriptMediaJSON[key]
		for each in val:
			try:
				if each["url"].endswith(".html") == True:
					pass

				else:
					imgUrl = 'http:%s' % each["url"]
					getImg = requests.get(imgUrl)
					jpgFileName = imgUrl.split('/')[-1]#.split('.')[0]

					with open('%s%s.jpg' % (upcDir, jpgFileName), 'wb') as dlImg: #Download and save main image
						dlImg.write(getImg.content)

			except:
				pass

	sellColors = scriptProductJSON['atsByColor']
	if sellColors == None:
		pass

	else:
		for key in sellColors:
			if key == "isMarkedDown" or key == 'installPrice' or key == 'currentPrice':
				pass

			else:
				if sellColors[key]["currentPrice"] == "":
					sellColors[key]["currentPrice"] = 0.00
					print('zero')
					
				elif sellColors[key]["qvcPrice"] == "":
					sellColors[key]["qvcPrice"] = 0.00
					print('zero')

				else:
					curPrice = sellColors[key]["currentPrice"]
					qvcPrice = sellColors[key]["qvcPrice"]
					continue