#!/usr/bin/env python

import sys
import urllib2
import simplejson as json
import numpy as np
import logging
import time

# class ErrorLog:
# 	def __init__(self, filename):
# 		self.filename = filename
# 		self.output = []

# 	def _add_illegal(self, url):
# 		self.output.append(url)

# 	def _log(self):
# 		err_log = open(self.filename, 'w')
# 		for url in self.output:
# 			err_log.write(url + '\n')
# 		err_log.close()


def main(argv):
	fetcher = urllib2.build_opener()
	searchTerm = argv[1]

	logger_filename = 'resource/protest_images/google/run.log'
	logging.basicConfig(filename=logger_filename, level=logging.DEBUG)
	img_count = 0

	start_time = time.time()
	all_urls = []  # used to check image redundancy
	all_filenames = []  # used to order images with the same name
	# for startIndex in pageIndex:
	startIndex = 0
	while img_count < 10:
		searchUrl = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q=' + searchTerm + '&start=' + str(startIndex)
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
			base = 'resource/protest_images/google/' + searchTerm + '/'
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
			fh = open(filename, 'w')
			try:
				raw_image = urllib2.urlopen(imageUrl).read()
			except Exception:
				# logger._add_illegal(imageUrl)
				logging.debug('Illegal URL at : ' + imageUrl)
				pass
			fh.write(raw_image)
			fh.close()
			all_urls.append(imageUrl)
			img_count += 1
			print 'Current image count : ', img_count

		time.sleep(5)
		startIndex += 1

	# logger._log()
	# all_urls_log = open('resource/protest_images/google/all_urls.txt', 'w')
	for url in all_urls:
		logging.info('Retrieved URL : ' + url)
	# 	all_urls_log.write(url + '\n')
	# all_urls_log.close()
	print ('Execution time : %s seconds' % (time.time() - start_time))

if __name__ == '__main__':
	main(sys.argv)

