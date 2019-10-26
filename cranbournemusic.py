import requests
from lxml import etree
import pdb
import sys
import csv
import json



session = requests.Session()

FILE_NAME = 'cranbournemusic.csv'
FIELD_NAMES = ['Name', 'SKU', 'Supplier ID', 'Price', 'Image URLs', 'Product URL']


def get_name(page_tree):
	try:
		return page_tree.xpath('.//section[@id="content"]//div[@class="summary-container"]//h2[@itemprop="name"]/text()')[0].strip()
	except:
		return ''

def get_sku(page_tree):
	try:
		return page_tree.xpath('.//section[@id="content"]//div[@class="summary-container"]//span[@class="sku"]/text()')[0].strip()
	except:
		return ''

def get_supplier_id(page_tree):
	try:
		text_arr = []

		for text in page_tree.xpath('.//section[@id="content"]//div[@class="summary-container"]//div[contains(text(), "Supplier Id: ")]/text()'):
			text_arr.append(text.replace('Supplier Id: ', '').strip())

		return ''.join(text_arr)
	except:
		return ''

def get_price(page_tree):
	try:
		return ''.join(page_tree.xpath('.//section[@id="content"]//div[@class="summary-container"]//p[@class="price"]//text()'))
	except:
		return ''

def get_image_urls(page_tree):
	try:
		return page_tree.xpath('.//section[@id="content"]//figure[@class="woocommerce-product-gallery__wrapper"]/div/a/@href')[0].strip()
	except:
		return ''

error_file = open('error.txt', 'a')
results_file = open(FILE_NAME, 'w')
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


def parse_cat_page(cat_page_url):
	page = 1

	while True:
		response = session.get('%s/page/%s/?product_count=500' % (cat_page_url, page))
		page_tree = etree.HTML(response.text.encode('utf8'))

		if not len(page_tree.xpath('.//ul[contains(@class, "products")]')):
			break

		for product_link in page_tree.xpath('.//ul[contains(@class, "products")]/li/a/@href'):
			try:
				parse_product_page(product_link)
			except:
				error_file.write(product_link + '\n')

		page += 1


cat_page_url_arr = [
	'https://www.cranbournemusic.com.au/product-category/guitar',
	'https://www.cranbournemusic.com.au/product-category/bass',
	'https://www.cranbournemusic.com.au/product-category/amps',
	'https://www.cranbournemusic.com.au/product-category/keyboards',
	'https://www.cranbournemusic.com.au/product-category/drums',
	'https://www.cranbournemusic.com.au/product-category/sound-reinforcement',
	'https://www.cranbournemusic.com.au/product-category/b-flat-clarinets',
	'https://www.cranbournemusic.com.au/product-category/presonus',
	'https://www.cranbournemusic.com.au/product-category/amebclarinet',
	'https://www.cranbournemusic.com.au/product-category/gaffa-tape'
]

for cat_page_url in cat_page_url_arr:
	parse_cat_page(cat_page_url)
	break

error_file.close()
results_file.close()