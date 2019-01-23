import glob,os,sys,json,datetime
import pandas as pd

class Environment:
    def __init__(self):
        self.envpath = "./environment.json"
        with open(self.envpath, "r", encoding='utf8') as env_file:
            env = json.loads(env_file.read())
            env_file.close()
        env_type = env["type"]
        self.new_datapath = env[env_type]["new_datapath"]
        self.old_datapath = env[env_type]["old_datapath"]
        self.keywords_path = env[env_type]["keywords_path"]
        self.acronyms_path = env[env_type]["acronyms_path"]
        self.filtered_datapath = env[env_type]["filtered_datapath"]
        self.polarity_datapath_clustered = env[env_type]["polarity_datapath_clustered"]
        self.polarity_datapath_categorized = env[env_type]["polarity_datapath_categorized"]
        self.densitymap_datapath = env[env_type]["densitymap_datapath"]
        self.cachepath = env[env_type]["cache_path"]
        self.since = env[env_type]["since"]
        self.until = datetime.datetime.now().strftime('%b %d %Y')
        self.mintime = env[env_type]["mintime"]
        self.maxtime = env[env_type]["maxtime"]
        self.max_stream = int(env[env_type]["max_stream"])
        self.months = env[env_type]["months"]
        self.aspect_categories = env[env_type]["aspect_categories"]
        self.stream_filters = env[env_type]["stream_filters"]
        self.tweet_consumer_key = env[env_type]["tweet_consumer_key"]
        self.tweet_consumer_secret = env[env_type]["tweet_consumer_secret"]
        self.tweet_access_token = env[env_type]["tweet_access_token"]
        self.tweet_access_token_secret = env[env_type]["tweet_access_token_secret"]
        self.aspect_type = env[env_type]["aspect_type"]
        self.cash_cleaner = env[env_type]["cash_cleaner"]

    def get_max_stream(self):
        return self.max_stream

    def get_new_datapath(self):
        return self.new_datapath

    def get_old_datapath(self):
        return self.old_datapath

    def get_keywords(self):
        keywords = []
        df = pd.read_csv(self.keywords_path, encoding="utf8")
        for word in df.iloc[:,1]:
            keywords.append(word)
        return keywords

    def get_acronyms(self):
        acronyms = {}
        df = pd.read_csv(self.acronyms_path, encoding="utf8", delimiter=";")
        for i in range(0, len(df.iloc[:,0])):
            acronyms[df.iloc[i,0].lower()] = df.iloc[i,1]
        return acronyms

    def get_filtered_datapath(self):
        return self.filtered_datapath

    def get_polarity_datapath_clustered(self):
        return self.polarity_datapath_clustered

    def get_polarity_datapath_categorized(self):
        return self.polarity_datapath_categorized

    def get_densitymap_datapath(self):
        return self.densitymap_datapath

    def get_cachepath(self):
        return self.cachepath

    def get_cache(self):
        with open(self.cachepath, "r", encoding='utf8') as cache_file:
            cache = json.loads(cache_file.read())
            cache_file.close()
        return cache

    def set_cache(self, cache):
        with open(self.cachepath, 'w', encoding='utf8') as cachefile:
            json.dump(cache,cachefile)
            cachefile.close()

    def get_census_tracts(self):
        censustracts = []
        for filename in glob.glob(self.filtered_datapath + '*.json'):
            censustracts.append(".".join(filename.split('/')[-1].split('.')[0:-1]))
        return censustracts

    def get_months(self):
        return self.months

    def get_aspect_categories(self):
        return self.aspect_categories

    def get_stream_filters(self):
        return self.stream_filters

    def get_aspect_type(self):
        return self.aspect_type

    def get_cash_cleaner(self):
        return self.cash_cleaner