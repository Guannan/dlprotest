#!/usr/bin/env python

import os
import sys, traceback
import urllib2
import requests
import simplejson as json
import numpy as np
import logging
import time

def get_img(url, search_term):
    dir_path = '../../resource/google/' + search_term + '/'
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + '/' + url.split('/')[-1]
    fh = open(file_path,'wb')
    try:
    	fh.write(requests.get(url).content)
    except Exception:
    	traceback.print_exc(file=sys.stdout)
    	logging.debug('Illegal URL at : ' + url)
    fh.close()

def main(argv):
	fetcher = urllib2.build_opener()
	search_term = argv[1]

	logger_filename = '../../resource/google/run.log'
	logging.basicConfig(filename=logger_filename, level=logging.DEBUG)
	img_count = 0

	start_time = time.time()
	all_urls = []  # used to check image redundancy
	all_filenames = []  # used to order images with the same name

	startIndex = 0
	while img_count < 64:  # google only allows 64 images per search term
		searchUrl = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + search_term + '&start=' + str(startIndex)
		f = fetcher.open(searchUrl)
		deserialized_output = json.load(f)

		try:
			results = deserialized_output['responseData']['results']
		except Exception:
			# in case of null response
			continue

		for result in results:
			imageUrl = result['unescapedUrl']
			if imageUrl in all_urls:
				continue
			base = 'resource/google/' + search_term + '/'
			if imageUrl.strip().split('/')[-1] == '':
				continue
			filename = base + imageUrl.strip().split('/')[-1]
			count = 2
			if filename in all_filenames:
				new_name = filename + str(count)
				while new_name in all_filenames:
					count += 1
					new_name = filename + str(count)
					if new_name not in all_filenames:
						filename = new_name

			all_filenames.append(filename)
			get_img(imageUrl, search_term)
			all_urls.append(imageUrl)
			img_count += 1
			print 'Current image count : ', img_count

		time.sleep(3)
		startIndex += 1

	for url in all_urls:
		logging.info('Retrieved URL : ' + url)
	print ('Execution time : %s seconds' % (time.time() - start_time))

if __name__ == '__main__':
	main(sys.argv)

