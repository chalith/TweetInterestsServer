import schedule, time, json, sys

from datetime import datetime, timedelta
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

from modules.scraper.scrape import *
from controller import Controller
#from tweetfilter import TweetFilter
#filter = TweetFilter()
controller = Controller()

app = Flask(__name__)
api = Api(app)

def periodic(scheduler, interval, action, actionargs=()):
    scheduler.enter(interval, 1, periodic,
                    (scheduler, interval, action, actionargs))
    action(*actionargs)

def job():
    print("Streaming tweets started")
    sinceScrape = (datetime.now()+timedelta(days=-1)).strftime('%Y-%m-%d')
    untilScrape = datetime.now().strftime('%Y-%m-%d')
    scrape(sinceScrape, untilScrape)
    print("Streaming tweets ended")
    print("Filtering tweets started")
    filter.readTweets()
    print("Filtering tweets ended")

def streamer():
    schedule.every().day.at("08:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def server():
    @app.route('/getpolarities')
    @cross_origin()
    def get_polarities():
        censustract = request.args.get('censustract')
        since = request.args.get('since')
        until = request.args.get('until')
        return json.dumps(controller.getPolarities(censustract,since,until))

    @app.route('/getcensusdata')
    @cross_origin()
    def get_censusdata():
        since = request.args.get('since')
        until = request.args.get('until')
        mintime = request.args.get('mintime')
        maxtime = request.args.get('maxtime')
        aspecttype = int(request.args.get('aspecttype'))
        return json.dumps(controller.getCensusdata(since,until,mintime,maxtime,aspecttype))

    @app.route('/getdensitymaps')
    @cross_origin()
    def get_densitymaps():
        since = request.args.get('since')
        until = request.args.get('until')
        mintime = request.args.get('mintime')
        maxtime = request.args.get('maxtime')
        return json.dumps(controller.getDensityMaps(since,until,mintime,maxtime))
    
    app.run(port='8000')

if __name__ == '__main__':
    #job()
    #filter.readTweets()
    server()
    # try:
    #     _thread.start_new_thread(streamer, ())
    #     _thread.start_new_thread(server, ())
    # except:
    #     print ("Error: unable to start thread")

    # while 1:
    #     pass