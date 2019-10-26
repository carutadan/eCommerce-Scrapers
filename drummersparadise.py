import requests
from lxml import etree
import pdb
import sys
import csv
import json



session = requests.Session()

FILE_NAME = 'drummersparadise.csv'
FIELD_NAMES = ['Name', 'SKU', 'Supplier ID', 'Price', 'Image URLs', 'Product URL']


def get_name(page_tree):
	try:
		return page_tree.xpath('.//div[@class="page-content"]//h1[@class="product-name"]/text()')[0].strip()
	except:
		return ''

def get_sku(page_tree):
	try:
		return page_tree.xpath('.//div[@class="page-content"]//div[@class="info-row sku"]/span/text()')[0].strip()
	except:
		return ''

def get_supplier_id(page_tree):
	return ''

def get_price(page_tree):
	try:
		return '$'+(page_tree.xpath('.//div[@class="page-content"]//span[@class="current-price price"]/span[@class="price-amount"]/text()')[0].strip())
	except:
		return ''

def get_image_urls(page_tree):
	try:
		return page_tree.xpath('.//div[@class="page-content"]//div[@class="product-widget widget-productImage "]//img/@src')[0].strip()
	except:
		return ''

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
		'Image URLs'	: 'https://www.drummersparadise.com.au%s' % get_image_urls(page_tree),
		'Product URL'	: product_link.strip()

	}

	print(product)
	writer.writerow(product)


def parse_category_page(cat_link):
	response = session.get(cat_link)

	tree = etree.HTML(response.text.encode('utf8'))

	sub_cat_link_arr = tree.xpath('.//div[@class="body"]//div[@class="content"]//a[contains(@class, "category-name-link")]/@href')
	product_link_arr = tree.xpath('.//div[@class="body"]//div[@class="content"]//div[@class="image product-image"]/a/@href')

	if len(sub_cat_link_arr):
		for sub_cat_link in sub_cat_link_arr:
			parse_category_page('https://www.drummersparadise.com.au%s' % sub_cat_link)
	elif len(product_link_arr):
		for product_link in product_link_arr:
			parse_product_page('https://www.drummersparadise.com.au%s' % product_link)


def parse_main_page(page_url):
	response = session.get(page_url)

	if response.status_code != 200:
		sys.exit('Status Code is not 200')


	tree = etree.HTML(response.text.encode('utf8'))
	cat_link_arr = tree.xpath('.//div[@class="nav-wrapper vertical"]//a[@class="category" and not(../span[contains(@class, "child-opener")])]/@href')

	for cat_link in cat_link_arr:
		parse_category_page('https://www.drummersparadise.com.au%s' % cat_link)



parse_main_page('https://www.drummersparadise.com.au/category/drums')
results_file.close()