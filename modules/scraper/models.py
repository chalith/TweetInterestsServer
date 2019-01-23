class Tweet(object):

    def __init__(self):
        pass


class TweetCriteria(object):

    def __init__(self):
        self.max_tweets = 100

    def set_username(self, username):
        self.username = username
        return self

    def set_since(self, since):
        self.since = since
        return self

    def set_until(self, until):
        self.until = until
        return self

    def set_query(self, query):
        self.query = query
        return self

    def set_geocode(self, geocode):
        self.geocode = geocode
        return self

    def set_max_tweets(self, max_tweets):
        self.max_tweets = max_tweets
        return self

    def set_language(self, language):
        self.language = language
        return self
