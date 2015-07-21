#!/usr/bin/env python

# source : https://gist.github.com/edsu/92225691402fbd21bc65

import json
import time
import logging
import requests
from bs4 import BeautifulSoup
import urllib2

global q 
q = "protest"
global key 
key = "09C43A9B270A470B8EB8F2946A9369F3"
global t0
t0  = 1407715200           # 11 Aug 2014 00:00:00 GMT
global end
end = t0 + (60 * 60 * 24 * 30 * 12) # 12 months after
global tweets
tweets = []
global image_count
image_count = 0

def get_img_link(url):
    """Gets the actual non-redirect link for the image
    """
    global image_count

    soup = BeautifulSoup(urllib2.urlopen(url).read())

    urls = []
    img_list = soup.findAll('meta', {"property":'og:image'})
    for og_image in img_list:
        if not og_image.get('content'):
            continue

        image_url = og_image['content']
        image_url = image_url.strip().split(':large')[0]
        urls.append(image_url)

    image_count += 1
    print 'Image count : ', image_count

    if urls:
        return urls[0]
    else:
        return None

def remove_retweet():
    global tweets
    tweets = [t for t in tweets if t['title'].replace('"','')[:2] != 'RT']

def main():
    global t0
    global end
    global tweets

    output = []
    logging.basicConfig(filename='topsy.log', level=logging.INFO)
    fh = open('topsy_output.txt', 'w')    
    
    try:
        while t0 < end:
            tweets = []
            results, t0, t1 = get_tweets(t0, 60 * 60 * 24 * 7)   # interval of 7 days
            for tweet in results:
                # t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tweet['firstpost_date']))

                tweet_url = ''
                title = ''
                img_link = ''

                if tweet['trackback_permalink'] is not None:
                    tweet_url = tweet['trackback_permalink']

                try:
                    title = tweet['title']   # pulling tweet titles
                    title = title.encode('ascii', errors='ignore')
                except Exception:
                    pass

                try:
                    exp_url = tweet['url_expansions'][0]['expanded_url']   # pulling photo links                    
                    if '/photo/' in exp_url:
                        img_link = exp_url
                        img_link = get_img_link(img_link)  # grabbing the meta tag content on tweets with images
                except Exception:
                    pass


                tweets.append({'url':tweet_url, 'title':title, 'img_link':img_link})

            t0 = t1

            remove_retweet()

            for tweet in tweets:
                try:
                    output = '\t'.join([tweet['url'],tweet['title'],tweet['img_link']])
                    fh.write(output + '\n')
                except Exception:
                    pass

    except requests.exceptions.ConnectionError:
        fh.close()
        sys.exit(1)
    fh.close()



def get_tweets(t0, interval):
    global q
    global key
    page = 1
    t1 = t0 + interval
    url = 'http://otter.topsy.com/search.json?q=%s&apikey=%s&perpage=100&mintime=%s&maxtime=%s&page=%s' % (q, key, t0, t1, page)
    print 'Search Page URL : ', url
    results = requests.get(url).json()
    total_results = results['response']['total']

    all_tweets = []
    while True:
        all_tweets += results['response']['list']
        page += 1
        if page < 4 and len(all_tweets) < total_results:
            time.sleep(1)
            print 'New Page'
            url = 'http://otter.topsy.com/search.json?q=%s&apikey=%s&perpage=100&mintime=%s&maxtime=%s&page=%s' % (q, key, t0, t1, page)
            print 'Search Page URL : ', url            
            results = requests.get(url).json()
        else:
            break
            
    return all_tweets, t0, t1

if __name__ == "__main__":
    main()



