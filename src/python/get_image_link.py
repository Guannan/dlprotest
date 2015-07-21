#!/usr/bin/env python

from bs4 import BeautifulSoup
import urllib2

def get_img_link(url):
	soup = BeautifulSoup(urllib2.urlopen(url).read())

	urls = []
	img_list = soup.findAll('meta', {"property":'og:image'})
	for og_image in img_list:
	    if not og_image.get('content'):
	        continue

	    image_url = og_image['content']
	    print image_url
	    image_url = image_url.strip().split(':')[0]
	    print image_url
	    urls.append(image_url)

	if urls:
		return urls[0]
	else:
		return None



