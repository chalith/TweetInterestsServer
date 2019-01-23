from modules.scraper.controllers import *
from modules.scraper.models import *
from modules.environment import Environment

environment = Environment()

def scrape(since, until):
    tweet_criteria = TweetCriteria()

    tweet_criteria.since = since
    tweet_criteria.until = until
    tweet_criteria.query = ' OR '.join(environment.get_stream_filters())
    #tweet_criteria.geocode = "43.082319,-79.072325,50km"
    tweet_criteria.geocode = "0,0,20016km"
    tweet_criteria.max_tweets = 200000

    filename = since+"-"+until+".txt"

    exporter = Exporter(environment.get_new_datapath()+filename)
    miner = Scraper()

    miner.get_tweets(tweet_criteria, buffer = exporter.output_to_file)
    exporter.close()

    text = 'Finished scraping data. Output file generated "'+filename+'"'
    print(text)