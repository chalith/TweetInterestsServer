import os
import time
import pandas as pd
import urllib.request
import json
from collections import Counter
from pprint import pprint


API_KEY = "MY_KEY"
API_HOST = "https://maps.googleapis.com/maps/api/place"
TEXT_SEARCH_PATH = "/textsearch"
DETAIL_SEARCH_PATH = "/details"
QUERY_TERM = "auto+repair+in+pittsburgh"
