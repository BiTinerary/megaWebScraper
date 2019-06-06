import requests, json, re
from selenium import webdriver
from bs4 import BeautifulSoup

def amz(webpage, upc, upcDir):
		browser = webdriver.Chrome()
		browser.get("%s%s" % (webpage, upc))
		html = browser.page_source
		soup = BeautifulSoup(html, 'lxml')
		pics = soup.find_all('li', class_="a-spacing-small item imageThumbnail a-declarative")
		imgLinks = [i.find_all("img") for i in pics]
		imgJpgs = set([i[0]["src"] for i in imgLinks])

		fullImg = []
		for i in imgJpgs:
			#if i.endswith(".jpg"):
				#i = re.sub('._SS\d\d_.', '.__.', i)
			fullImg.append(i)
		browser.close()

		print(fullImg)
		"""
		try:
			for i, each in enumerate(fullImg):
				getImg = requests.get(each)
				with open('%s/%s__%s.jpg' % (upcDir, each.split('/')[-1].replace(".jpg", ""), i), 'wb') as dlImg: #Download and save main image
					dlImg.write(getImg.content)
				print 'Downloaded picture #%s' % i
		except:
			pass
		"""