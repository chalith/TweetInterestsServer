from datetime import datetime, timedelta
from modules.scraper.scrape import *

sinceScrape = datetime.strptime("2018-12-14",'%Y-%m-%d')
untilScrape = datetime.strptime("2019-01-01",'%Y-%m-%d')

while sinceScrape<untilScrape:
    curuntil = sinceScrape+timedelta(weeks=1)
    scrape(sinceScrape.strftime('%Y-%m-%d'), curuntil.strftime('%Y-%m-%d'))
    sinceScrape = curuntil
