import requests
from lxml import etree
import pdb
import sys
import csv
import json



session = requests.Session()

FILE_NAME = 'drumtek.csv'
FIELD_NAMES = ['Name', 'SKU', 'Supplier ID', 'Price', 'Image URLs', 'Product URL']


def get_name(page_tree):
	try:
		return page_tree.xpath('//div[@class="ContentArea"]/h1[@class="title"]/text()')[0].strip()
	except:
		return ''

def get_sku(page_tree):
	try:
		return page_tree.xpath('//div[@class="ContentArea"]//span[@class="VariationProductSKU"]/text()')[0].strip()
	except:
		return ''

def get_supplier_id(page_tree):
	return ''

def get_price(page_tree):
	try:
		return page_tree.xpath('//div[@class="ContentArea"]//em[@class="ProductPrice VariationProductPrice"]/text()')[0].strip()
	except:
		return ''

def get_image_urls(page_tree):
	try:
		image_urls = []

		for json_str in page_tree.xpath('//div[@class="ContentArea"]//div[@class="TinyOuterDiv"]//a/@rel'):
			json_data = json.loads(json_str)

			try:
				image_urls.append(json_data['largeimage'].split('?')[0].strip())
			except:
				pass

		return '\n'.join(image_urls)
	except:
		return ''

with open(FILE_NAME, 'w') as results_file:
	writer = csv.DictWriter(results_file, fieldnames=FIELD_NAMES)
	writer.writeheader()


	def parse_product_page(product_link):
		response = session.get(product_link)
		page_tree = etree.HTML(response.text.encode('utf8'))

		product = {
			'Name'			: get_name(page_tree),
			'SKU'			: get_sku(page_tree),
			'Supplier ID'	: get_supplier_id(page_tree),
			'Price'			: get_price(page_tree),
			'Image URLs'	: get_image_urls(page_tree),
			'Product URL'	: product_link.strip()

		}

		print(product)
		writer.writerow(product)


	def parse_brand_page(brand_link):
		page = 1

		while True:
			response = session.get('%s?page=%s' % (brand_link, page))
			page_tree = etree.HTML(response.text.encode('utf8'))

			if not len(page_tree.xpath('.//form[@id="frmCompare"]/ul[@class="ProductList"]')):
				break

			for product_link in page_tree.xpath('.//form[@id="frmCompare"]/ul[@class="ProductList"]/li/div[contains(@class, "ProductImage")]/a/@href'):
				parse_product_page(product_link)

			page += 1



	response = session.get('https://www.drumtek.com.au/brands/')

	if response.status_code != 200:
		sys.exit('Status Code is not 200')
		

	tree = etree.HTML(response.text.encode('utf8'))

	for brand_link in tree.xpath('.//div[@class="BrandImage"]/a/@href'):
		parse_brand_page(brand_link)