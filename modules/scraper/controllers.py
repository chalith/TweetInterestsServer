import sys, json, re, codecs, urllib.parse
import requests as req
import tweepy
from datetime import datetime
from pyquery import PyQuery as pq
from .models import Tweet, TweetCriteria

CONSUMER_KEY = "XSZdfeTaZboGh7Gb93Ny6Qcrt"
CONSUMER_SECRET = "aHnHBNDlX9g43H9XCZmpIsmUXYSi2IvQHgrwlMBVeE6V857BQS"
OAUTH_TOKEN = "309718769-bGVcX1VSJubYzOlwOWaqjN3gP5jaorAaY2wi13Wb"
OAUTH_TOKEN_SECRET = "SNsPk87slxuLL75KEXMIDavDzyok7rlDrbP28sDBN3Cfc"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
api = tweepy.API(auth)

class Exporter(object):

    def __init__(self, filename):
        self.filename = filename
        self.output = codecs.open(self.filename, 'w+', 'utf-8')

    def output_to_file(self, tweets):
        for tweet in tweets:
            json.dump(tweet, self.output)
            self.output.write("\n")
        self.output.flush()
        print ('%d tweets added to file' % len(tweets))

    def close(self):
        self.output.close()

class Scraper(object):

    def __init__(self):
        pass

    @staticmethod
    def set_headers(data, language, refresh_cursor):
        url = 'https://twitter.com/i/search/timeline?f=realtime&q=%s&src=typd'\
                + '&%smax_position=%s'
        url = url % (urllib.parse.quote(data), language, refresh_cursor)
        headers = {
            'Host': 'twitter.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'de,en-US;q=0.7,en;q=0.3',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': url,
            'Connection': 'keep-alive'
        }

        return url, headers

    @staticmethod
    def filter_Tweet(tweet):
        if((tweet.get("retweeted_status"))
        or (tweet.get("in_reply_to_status_id"))
        or (tweet.get("in_reply_to_status_id_str"))
        or (tweet.get("in_reply_to_user_id"))
        or (tweet.get("in_reply_to_user_id_str"))
        or (tweet.get("in_reply_to_screen_name"))
        or (not tweet.get("geo"))):
            return False
        return True

    @staticmethod
    def get_tweets(tweet_criteria, buffer = None, buffer_length = 10):
        active = True
        refresh_cursor = ''
        mentions = re.compile('(@\\w*)')
        hashtags = re.compile('(#\\w*)')
        results = []
        results_to_append = []

        if tweet_criteria.max_tweets <= 0:
            return

        while active:
            json = Scraper.get_json_response(tweet_criteria, refresh_cursor)

            if not json or len(json['items_html'].strip()) == 0:
                break

            refresh_cursor = json['min_position']
            tweets = pq(json['items_html'])('div .js-stream-tweet')

            if len(tweets) == 0:
                break

            for tweetHTML in tweets:
                _ = pq(tweetHTML)
                tweet_id = _.attr('data-tweet-id')
                
                tweet = api.get_status(tweet_id)._json


                if not Scraper.filter_Tweet(tweet):
                    continue

                results.append(tweet)
                results_to_append.append(tweet)

                if buffer and len(results_to_append) >= buffer_length:
                    buffer(results_to_append)
                    results_to_append = []

                if len(results) >= tweet_criteria.max_tweets:
                    active = False
                    break

        if buffer and len(results_to_append) > 0:
            buffer(results_to_append)

        return results

    @staticmethod
    def get_json_response(tweet_criteria, refresh_cursor):
        data = ' -filter:retweets'

        if hasattr(tweet_criteria, 'username'):
            data += ' from:' + tweet_criteria.username

        if hasattr(tweet_criteria, 'since'):
            data += ' since:' + tweet_criteria.since

        if hasattr(tweet_criteria, 'until'):
            data += ' until:' + tweet_criteria.until

        if hasattr(tweet_criteria, 'geocode'):
            data += ' geocode:' + tweet_criteria.geocode
	
        if hasattr(tweet_criteria, 'query'):
            data += ' ' + tweet_criteria.query
	    
        else:
            print('No query placed.')
            return

        if hasattr(tweet_criteria, 'language'):
            language = 'lang=' + tweet_criteria.language + '&'
        else:
            language = 'lang=en-US&'

        url, headers = Scraper.set_headers(data, language, refresh_cursor)

        try:
            r = req.get(url, headers=headers)
        except:
            text = 'Twitter weird response. Try to see on browser:'\
                    +'https://twitter.com/search?q=%s&src=typd'
            print(text % urllib.parse.quote(url))
            print('Unexpected error:', sys.exc_info()[0])
            sys.exit()
            return

        return r.json()
