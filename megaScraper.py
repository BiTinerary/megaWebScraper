import json, sys, os, re
import pandas as pd

inDir = './input/'
outDir = './output/'
site = 'homedepot'#sys.argv[2]
spreadsheet = 'dfIn.csv'#sys.argv[3]
dfIn = "%s%s" % (inDir, spreadsheet)
# ie: Scrape Site With This

class eCommTools():
	def __init__(self, site, df):
		
		self.site = site

		if df.endswith('.xlsx'): # If excel file, ie: default Walmart sales export
			self.df = pd.read_excel(df)
		elif df.endswith('.csv'): # If csv file, ie: default Ebay sales export
			self.df = pd.read_csv(df, encoding='cp1252', dtype=str)
		elif df.endswith('.txt'): # If tabulated .txt file, ie: Default Amazon sales export.
			self.df = pd.read_table(df, encoding='cp1252')

		if self.site == 'evine':
			from scrapers.evn import evn
			self.scraperFunction = evn
	
			self.webpagePrefix = 'https://www.evine.com/Product/'
			self.alnumRegex = re.compile("""[^a-zA-Z0-9&"'. ]""")#re.compile('[^a-zA-Z]')
			self.evineJS = re.compile('clientSideData={.*?};', re.DOTALL) # compile regex for parsing out the raw syntax of json data
			
		elif self.site == 'qvc':
			from scrapers.qvc import qvc
			self.scraperFunction = qvc
	
			self.webpagePrefix = 'https://www.qvc.com/product.'
			self.qvcJS = re.compile('utag_data={.*?};', re.DOTALL)
	
		elif self.site == 'homedepot':
			from scrapers.thd import thd
			self.scraperFunction = thd
	
			self.upcList = set([row['UPC'] for index, row in self.df.iterrows()])
			self.webpagePrefix = 'https://www.homedepot.com/s/'

	def scrape(self):
		def noDuplicates(upc):
			if not os.path.exists(self.upcDir): # File/folder doesn't exist for current productID, create it and scrape it.
				os.makedirs(self.upcDir)
				self.scraperFunction(self.webpagePrefix, upc, self.upcDir)

			else:
				print('Folder for this UPC already exists.\n')
				pass

		counter = 1
		maxCounter = len(self.upcList)
		for upc in self.upcList:
			self.upcDir = './output/%s/%s/' % (self.site, upc)
			
			try: # readable stdout with minimal progress counter
				print('Downloading %s - %s/%s' % (upc, counter, maxCounter))
				noDuplicates(upc)
				
			except Exception as e: # If SKU url doesn't exist, print error then pass to next one.
				print('%s\nThere was an error scraping: "%s"\n' % (e, upc))
				pass

			finally: # increment progress counter
				counter += 1
				print "\n"

	def dfOutput(self):
		"Use class dfIn as reference for generating output spreadsheet if relevant product present in output/scraped folders"
		if site == 'homedepot':
			for index, row in self.df.iterrows():
				upc = str(row["UPC"])
				try:
					with open('./output/%s/%s/%s-CustomInfo.json' % (site, upc, upc), 'r') as customLog: 
						jLog = json.load(customLog)
						self.df.loc[index, "Title"] = '=HYPERLINK("%s", "%s %s - %s")' % (jLog['productUrl'], jLog['brand'], jLog['title'], jLog['model'].replace("Model: ", ""))
						#self.df.loc[index, "Hyperlink"] = jLog['productUrl']
						self.df.loc[index, 'Model'] = jLog['model'].replace("Model: ", "")
						self.df.loc[index, 'UPC'] = jLog["upc"]
						self.df.loc[index, 'Retail'] = jLog['retail']
						self.df.loc[index, 'Brand'] = jLog['brand']
						self.df.loc[index, 'StoreSku'] = jLog['storeSku']
						#self.df.loc[index, 'Description'] = re.sub(r'[^\x00-\x7F]+',' ', jLog['description'])
				except Exception as e:
					print('No scrape file for PID: "%s"' % upc)
					print(e)
					pass
			self.df = self.df[['Title', 'Model', 'Brand', 'StoreSku', 'UPC', 'Retail']]
		self.df.to_csv('./output/dfOut.csv', index=False)
		self.df.to_excel('./output/dfOut.xlsx', index=False)
		print('New Spreadsheet Generated!')
			
	def sales():
		"parse sales per vender-brand-upc-grade"
		def taxes():
			"while gathering sales data, give option to output quarterly tax info"


if __name__ == "__main__":
	e = eCommTools(site, dfIn)
	e.scrape()
	e.dfOutput()
