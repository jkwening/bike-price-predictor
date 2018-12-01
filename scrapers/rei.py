"""
Module for scraping rei.com for its bike data.
"""
import os
import math
import json

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH, TIMESTAMP
from scrapers.scraper_utils import get_bike_type_from_desc


class Rei(Scraper):
  def __init__(self, save_data_path=DATA_PATH, page_size=90):
    self._page_size = page_size
    self._BIKE_ENDPOINTS = {
      'road': 'road-bikes',
      'mountain': 'mountain-bikes',
      'cyclocross': 'cyclocross-bikes',
      'adventure': 'adventure-bikes',
      'touring': 'touring-bikes',
      'urban': 'urban-bikes',
      'track': 'track-bikes',
      'single-speed': 'single-speed-bikes',
      'time-trial': 'time-trial-bikes',
      'bmx': 'bmx-bikes',
      'kid': 'kids-bikes'
    }
    super().__init__(base_url='http://www.rei.com',
      source='rei', save_data_path=save_data_path)
  
  def _fetch_prod_listing_view(self, page=1, page_size=90):
    endpoint = 'search-ui/rest/search/products/results?'
    r = 'category%3Abikes'
    sx = 'vF%2BF6Nv%2Fywwl9uqxBg%2FvKQ%3D%3D'
    origin = 'web'
    req_url = f'{self._BASE_URL}/{endpoint}r={r}&sx={sx}&origin={origin}&page={page}&pagesize={page_size}'
    return self._fetch_html(req_url)

  #TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
  def _get_max_num_prods(self):
    """Get total number of products available."""
    data = json.loads(self._fetch_prod_listing_view(page_size=self._page_size))
    return int(data['query']['totalResults'])

  def _parse_prod_specs(self, soup):
    """Return dictionary representation of the product's specification."""
    prod_specs = dict()
    try:
      script_product_details = soup.find('script',
        attrs={'data-client-store': 'product-details'})
      data = json.loads(script_product_details.string)
      specs = data['specs']

      # Get each spec_name, value pairing for bike product
      for spec in specs:
        name = spec['name']
        value = spec['values'][0]
        spec_name = self._normalize_spec_fieldnames(name)
        prod_specs[spec_name] = value
        self._specs_fieldnames.add(spec_name)
      
      print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
    except AttributeError as err:
      print(f'\tError: {err}')

    return prod_specs

  def get_all_available_prods(self, to_csv=True) -> list:
    """Scrape wiggle site for prods."""
    # Reset scraper related variables
    self._products = dict()
    self._num_bikes = 0

    # Get first bike page as json and determine total number of products pages to scrape
    page_num = 1
    data = json.loads(self._fetch_prod_listing_view(page_size=self._page_size))
    num_pages = math.ceil(int(data['query']['totalResults']) / int(data['query']['upperResult']))

    # Scrape first page while its in memory then fetch and scrape the remaining pages
    while True:
      results = data['results']

      for prod in results:
        product = {'site': 'rei'}
        brand = prod['brand']
        title = prod['cleanTitle']
        product['brand'] = brand
        product['description'] = f'{brand} {title}'
        product['product_id'] = prod['prodId']
        product['href'] = prod['link']
        display_price = prod['displayPrice']
        product['price'] = display_price['max']
        product['msrp'] = display_price['compareAt']
        self._products[prod['prodId']] = product
        print(f'[{len(self._products)}] New bike: ', product)

      self._num_bikes = len(self._products)
      print(f'Current number of products: {self._num_bikes}')

      page_num += 1
      if page_num > num_pages:
        break
      else:
        data = json.loads(self._fetch_prod_listing_view(page=page_num,
          page_size=self._page_size))

    if to_csv:
      return [self._write_prod_listings_to_csv()]

    return list()

  #TODO: remove this method and embed within get_all_available_prods
  # then remove from scraper module.
  def _get_prods_on_current_listings_page(self, data):
    pass
