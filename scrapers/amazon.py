import requests, json
from selenium import webdriver
from bs4 import BeautifulSoup

def amzn(webpage, upc, upcDir):
		browser = webdriver.Chrome()
		browser.get("%s%s" % (webpage, upc))
		html = browser.page_source
		soup = BeautifulSoup(html, 'lxml')
		pics = soup.find_all('li', class_="a-spacing-small item imageThumbnail a-declarative")
		imgLinks = [i.find_all("img") for i in pics]
		imgJpgs = [i[0]["src"] for i in imgLinks]

		for i in imgJpgs: print i