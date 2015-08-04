#!/usr/bin/env python

import os
import sys
import json
import time
import logging
import requests
import argparse
import traceback
from bs4 import BeautifulSoup

global key 
key = "09C43A9B270A470B8EB8F2946A9369F3"
global t0
# t0  = 1407715200           # 11 Aug 2014 00:00:00 GMT
global end
# end = t0 + (60 * 60 * 24 * 30 * 12) # 12 months after
global interval
global query

def get_img_link(url):
    """Gets the actual non-redirect link for the image
    """

    soup = BeautifulSoup(requests.get(url).text)

    urls = []
    img_list = soup.findAll('meta', {"property":'og:image'})
    for og_image in img_list:
        if not og_image.get('content'):
            continue

        image_url = og_image['content']
        image_url = image_url.strip().split(':large')[0]
        urls.append(image_url)

    if urls:
        return urls[0]
    else:
        return None

def get_img(tweet_dict):
    """Obtain folder path to save the retrieved image.
        Call retrieval helper function to pull image.
    """
    permalink = tweet_dict['url']
    arr = permalink.strip().split('/')
    user = arr[3]
    num = arr[-1]
    img_link = tweet_dict['img_link']
    if img_link:
        _get_img(img_link, user + '_' + num)

def _get_img(url, dir_path):
    """Helper function for actual pulling image from url
    """
    global query

    base_path = '../../resource/topsy/' + query + '/'
    dir_path = base_path + dir_path
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + '/' + url.split('/')[-1]
    fh = open(file_path,'wb')
    fh.write(requests.get(url).content)
    fh.close()

def remove_retweet(tweets):
    """Attempts to remove retweets through searching for RT
    """
    tweets = [t for t in tweets if t['title'].replace('"','')[:2] != 'RT']

def output_tweets(filename, tweets):
    """Output tweets related information into tab-delimited file
        Information include the permalink of tweet, title, and the image link if applicable
    """
    fh = open(filename, 'w')    
    for tweet in tweets:
        try:
            output = '\t'.join([tweet['url'],tweet['title'],tweet['img_link']])
            fh.write(output + '\n')
        except Exception:
            fh.close()

def main(argv):
    """Main. Retrieves tweets using the Topsy Otter API.
    """
    global t0
    global end
    global interval
    global query

    output = []
    # logging.basicConfig(filename=argv[3], level=logging.INFO)
    logging.basicConfig(filename='debug.log', level=logging.INFO)    
    output_filename = 'topsy_output.txt'

    q = query.strip().split('+')
    q = ' '.join(q)
    tweets = []
    tweet_count = 0
    try:
        while t0 < end and tweet_count < 10000:
            tweets = []
            results, t0, t1 = get_tweets(q, t0, interval)   # interval in seconds
            for tweet in results:
                # t = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(tweet['firstpost_date']))

                tweet_url = ''
                title = ''
                content = ''
                img_link = ''
                user = ''
                num = ''

                if tweet['trackback_permalink'] is not None:
                    tweet_url = tweet['trackback_permalink']
                    # print tweet_url

                if tweet['title'] is not None:
                    title = tweet['title']   # pulling tweet titles
                    title = title.encode('ascii', errors='ignore')

                if tweet['content'] is not None:
                    content = tweet['content']
                    title = title.encode('ascii', errors='ignore')                    

                try:
                    exp_url = tweet['url_expansions'][0]['expanded_url']   # pulling photo links
                    if '/photo/' in exp_url:
                        img_link = exp_url
                        img_link = get_img_link(img_link)  # grabbing the meta tag content on tweets with images
                except Exception:
                    img_link = ''

                if title and content and img_link:
                    tweets.append({'url':tweet_url, 'title':title, 'content':content, 'img_link':img_link})
                    tweet_count += 1

            t0 = t1

            remove_retweet(tweets)
            for tweet in tweets:
                get_img(tweet)
            output_tweets(output_filename, tweets)

    except requests.exceptions.ConnectionError:
        print(traceback.format_exc())
        sys.exit(1)



def get_tweets(q, t0, interval):
    """Retrieves tweets in JSON format
    """
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
        if page < 7 and len(all_tweets) < total_results:
            time.sleep(1)
            print 'New Page'
            url = 'http://otter.topsy.com/search.json?q=%s&apikey=%s&perpage=100&mintime=%s&maxtime=%s&page=%s' % (q, key, t0, t1, page)
            print 'Search Page URL : ', url
            results = requests.get(url).json()
        else:
            break
            
    return all_tweets, t0, t1

if __name__ == "__main__":
    global t0
    global end
    global interval
    global query

    parser = argparse.ArgumentParser(description = 'Topsy tweet retrieval')
    parser.add_argument('--query', metavar='query', type=str, help='Query term for Topsy')
    parser.add_argument('--start_time', metavar='int', type=int, help='Starting time for collected tweets: need converted number')
    parser.add_argument('--end_time', metavar='int', type=int, help='Ending time for collected tweets: need converted number')
    parser.add_argument('--interval', metavar='int', type=int, help='Interval for collected tweets: need number here in seconds')
    args = parser.parse_args()

    query = args.query
    t0 = args.start_time
    end = args.end_time
    interval = args.interval
    main(sys.argv)



