import json, time

from opinionminer import OpinionMiner
from datetime import datetime, timedelta
from densitymaps import DensityMaps
from modules.environment import Environment
from modules.geolocations import *
from modules.aspect import *
environment = Environment()

class Controller():
    def __init__(self):
        self.aspectObj = Aspect()

    def getFilteredCensustracts(self, index):
        cache = environment.get_cache()
        censustracts = cache["new_filtered_data"][index]
        return censustracts

    def clearFilteredCensustracts(self, index):
        cache = environment.get_cache()
        cache["new_filtered_data"][index] = []
        environment.set_cache(cache)
                    
    def getPolarities(self, censustract):
        opinionminer = OpinionMiner(censustract)
        return opinionminer.getPolarities()

    def getCensusdata(self, since=environment.since, until=environment.until, mintime=environment.mintime, maxtime=environment.maxtime, aspecttype=environment.aspect_type["cluster"]):
        censustracts = environment.get_census_tracts()
        polarities = {}
        if aspecttype == environment.aspect_type["cluster"]:
            newcensustacts = self.getFilteredCensustracts(environment.cash_cleaner["cluster"])
            polarity_datapath = environment.polarity_datapath_clustered
        elif aspecttype == environment.aspect_type["categorize"]:
            newcensustacts = self.getFilteredCensustracts(environment.cash_cleaner["categorize"])
            polarity_datapath = environment.polarity_datapath_categorized
        for idx,censustract in enumerate(censustracts):
            print("Loading : "+str(idx), end="\r")
            infile = False
            if censustract not in newcensustacts:
                try:
                    infile = open(polarity_datapath+censustract+".json", 'r', encoding='utf8')
                except:
                    pass
            if infile:
                print("reading...", end='\r')
                polrts = json.loads(infile.read())
                infile.close()
            else:
                opinionminer = OpinionMiner(censustract)
                polrts = opinionminer.getPolarities()
                if polrts:
                    temppolrts = {}
                    for date, pol in polrts.items():
                        for key, val in pol.items():
                            if key not in temppolrts:
                                temppolrts[key] = 0
                    if aspecttype == environment.aspect_type["cluster"]:
                        temppolrts = self.aspectObj.clusterAspects(temppolrts)
                    elif aspecttype == environment.aspect_type["categorize"]:
                        temppolrts = self.aspectObj.categorizeAspects(temppolrts)
                    returnpol = {}
                    for date, pol in polrts.items():
                        returnpol[date] = {}
                        for categ, aspcts in temppolrts.items():
                            for key, val in pol.items():
                                if key in aspcts:
                                    if categ not in returnpol[date]:
                                        returnpol[date][categ] = {}
                                    returnpol[date][categ][key] = val
                    polrts = returnpol
                with open(polarity_datapath+censustract+".json", 'w', encoding='utf8') as outfile:
                    print("writing...", end="\r")
                    json.dump(polrts, outfile)
                    outfile.close()
                    if aspecttype == environment.aspect_type["cluster"]:
                        self.clearFilteredCensustracts(environment.cash_cleaner["cluster"])
                    elif aspecttype == environment.aspect_type["categorize"]:
                        self.clearFilteredCensustracts(environment.cash_cleaner["categorize"])
            if polrts:
                for date in list(polrts):
                    tweetdate = datetime.strptime(date,"%a %b %d %H:%M:%S +0000 %Y")
                    if tweetdate < datetime.strptime(since, '%b %d %Y') or tweetdate > (datetime.strptime(until,'%b %d %Y')+timedelta(days=1)):
                        del polrts[date]
                    elif datetime.strptime(str(tweetdate.hour)+":"+str(tweetdate.minute), '%H:%M') < datetime.strptime(mintime, '%H:%M') or datetime.strptime(str(tweetdate.hour)+":"+str(tweetdate.minute), '%H:%M') > datetime.strptime(maxtime, '%H:%M'):
                        del polrts[date]
                if len(polrts)>0:
                    polarities[censustract] = {}
                    censusinfo = censustract.split("_")
                    polarities[censustract]['censusinfo'] = {
                        "tract" : censusinfo[0],
                        "city" : censusinfo[1],
                        "country" : censusinfo[2]
                    }
                    polarities[censustract]['polarities'] = polrts
        return polarities

    def getDensityMaps(self, since=environment.since, until=environment.until, mintime=environment.mintime, maxtime=environment.maxtime):
        newcensustacts = self.getFilteredCensustracts(environment.cash_cleaner["density"])
        censustracts = environment.get_census_tracts()
        maps = {}
        for idx,censustract in enumerate(censustracts):
            print("Loading : "+str(idx), end="\r")
            infile = False
            if censustract not in newcensustacts:
                try:
                    infile = open(environment.densitymap_datapath+censustract+".json", 'r', encoding='utf8')
                except:
                    pass
            if infile:
                print("reading...", end='\r')
                dmaps = json.loads(infile.read())
                infile.close()
            else:
                densityMaps = DensityMaps(censustract)
                #dmaps = densityMaps.getDensityMap()
                dmaps = densityMaps.getCoordinates()
                with open(environment.densitymap_datapath+censustract+".json", 'w', encoding='utf8') as outfile:
                    print("writing...", end="\r")
                    json.dump(dmaps, outfile)
                    outfile.close()
                    self.clearFilteredCensustracts(environment.cash_cleaner["density"])
            if dmaps:
                for date in list(dmaps):
                    tweetdate = datetime.strptime(date,"%a %b %d %H:%M:%S +0000 %Y")
                    if tweetdate < datetime.strptime(since, '%b %d %Y') or tweetdate > (datetime.strptime(until,'%b %d %Y')+timedelta(days=1)):
                        del dmaps[date]
                    elif datetime.strptime(str(tweetdate.hour)+":"+str(tweetdate.minute), '%H:%M') < datetime.strptime(mintime, '%H:%M') or datetime.strptime(str(tweetdate.hour)+":"+str(tweetdate.minute), '%H:%M') > datetime.strptime(maxtime, '%H:%M'):
                        del dmaps[date]
                if len(dmaps)>0:
                    maps[censustract] = {}
                    censusinfo = censustract.split("_")
                    maps[censustract]['censusinfo'] = {
                        "tract" : censusinfo[0],
                        "city" : censusinfo[1],
                        "country" : censusinfo[2]
                    }
                    maps[censustract]['map'] = dmaps
        return maps
