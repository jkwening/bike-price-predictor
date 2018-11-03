"""Modules for loading raw data files into appropriate tables in the database"""

from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.nashbar import NashBar
from scrapers.performance_bike import PerformanceBikes

SOURCES = [
  'performance', 'nashbar', 'competitive'
]

def main():
  # scrape data for each source and bike type
  for source in SOURCES:
    if source == 'performance':
      scraper_inst = PerformanceBikes()

    if source == 'nashbar':
      scraper_inst = NashBar()

    if source == 'competitive':
      scraper_inst = CompetitiveCyclist()

    scraper_inst.get_product_specs()
    
  # update manifest.csv accordingly to ensure its current
  # load data files into appropriate tables in database
  # - only load new values or update information changes for existing prods
  pass


if __name__ == '__main__':
  main()
