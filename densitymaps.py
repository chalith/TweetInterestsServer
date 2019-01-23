import json,time
import matplotlib.pyplot as plt
import pandas as pd

from datetime import datetime
from modules.geolocations import *
from modules.environment import Environment
environment = Environment()

class DensityMaps():
    def __init__(self, censustract):
        self.environment = environment
        self.censustract = censustract
        self.census_tweets = {}
        self.months = environment.get_months()
        with open(environment.filtered_datapath+censustract+".json", 'r', encoding='utf8') as tweetfile:
            for user, tweets in json.loads(tweetfile.read()).items():
                for tweet in tweets:
                    #date = datetime.strptime(tweet["datetime"],"%a %b %d %H:%M:%S +0000 %Y")
                    #key = self.months[date.month-1]+"-"+str(date.year)
                    key = tweet["datetime"]
                    if key not in self.census_tweets:
                        self.census_tweets[key] = []
                    self.census_tweets[key].append(tweet)
            tweetfile.close()
        
    def generateDataFrame(self):
        users = []
        latitude = []
        longitude = []
        for key,tweets in self.census_tweets.items():
            for tweet in tweets:
                if not tweet.get("user_id") in users:
                    users.append(tweet.get("user_id"))
                    latitude.append(tweet.get("location").get("coordinates")[0])
                    longitude.append(tweet.get("location").get("coordinates")[1])
        df = pd.DataFrame(
            {'User': users,
            'Latitude': latitude,
            'Longitude': longitude})
        if(len(self.census_tweets)>0):
            return df
        else:
            return False

    def generateJSON(self):
        maps = {}
        for key,tweets in self.census_tweets.items():
            objects = []
            for tweet in tweets:
                curobject = {
                        "user": tweet.get("user_id"),
                        "text": tweet.get("text"),
                        "datetime": tweet.get("datetime"),
                        "latitude": tweet.get("location").get("coordinates")[0],
                        "longitude": tweet.get("location").get("coordinates")[1]
                    }
                if not curobject in objects:
                    objects.append(curobject)
            maps[key] = objects
        if(len(self.census_tweets)>0):
            return maps
        else:
            return False
        
    def getDensityMap(self):
        densityMap = generateDensityMap(self.generateDataFrame())
        return densityMap

    def getCoordinates(self):
        return self.generateJSON()