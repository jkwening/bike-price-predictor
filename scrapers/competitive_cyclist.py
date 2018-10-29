import os
from bs4 import BeautifulSoup
from .scraper import Scraper
from .scraper_utils import DATA_PATH, TIMESTAMP


class CompetitiveCyclist(Scraper):
  def __init__(self, page_size=42):
    self._page_size = page_size
    self._bike_endpoints = {
      'road': 'road-bikes',
      'mountain': 'mountain-bikes',
      'cyclocross': 'cyclocross-bikes',
      'triathlon': 'triathlon-bike',
      'fat': 'fat-bikes',
      'kids': 'kids-bikes'
    }
    super().__init__(base_url='https://www.competitivecyclist.com',
      prod_spec_fname='competitive_prod_specs',
      prod_listing_fname='competitive_prod_listing')
  
  def _fetch_prod_listing_view(self, bike_type='road', page=0, page_size=42):
    req_url = f'{self._BASE_URL}/{self._bike_endpoints[bike_type]}?page={page}&pagesize={page_size}'
    return self._fetch_html(req_url)

  def _get_num_pages(self, soup):
    """Get number of result pages for products listsing."""
    page_num_links = soup.find_all('li', 'page-number')
    last_page_num_link = page_num_links.pop()
    return int(last_page_num_link.a.contents[0])


  def _get_max_num_prods(self, soup):
    """Get number of pages instead since number of products not easily presented."""
    return self._get_num_pages

  def _get_prods_on_current_listings_page(self, soup):
    div_id_products = soup.find('div', attrs={'id': 'products'})
    div_products_list = div_id_products.find_all('div', class_='product')

    for prod_info in div_products_list:
      product = dict()

      # get id
      prod_id = prod_info['data-product-id']
      product['id'] = prod_id
      
      # get page href
      prod_href = prod_info.a['href']
      product['href'] = prod_href
      
      # get brand
      prod_brand = prod_info.find('span', class_='ui-pl-name-brand').contents[0]
      product['brand'] = prod_brand
      
      # get desc
      prod_desc = prod_info.find('span', class_='ui-pl-name-title').contents[0]
      product['desc'] = prod_desc
      
      # get current and msrp price
      prod_retail = prod_info.find('span', class_='price-retail')

      if prod_retail is not None:
        retail = prod_retail.contents[0]
        prod_price = retail
        prod_msrp = prod_price
      else:
        prod_price = prod_info.find('span', class_='ui-pl-pricing-low-price').contents[0]
        prod_msrp = prod_info.find('span', class_='ui-pl-pricing-high-price').contents[0]

      product['price'] = prod_price
      product['msrp'] = prod_msrp

      self._products[prod_id] = product
      print(f'[{len(self._products)}] New bike: ', product)
  
  def _parse_prod_specs(self, soup):
    """Return dictionary representation of the product's specification."""
    div_tech_specs_section = soup.find('div', class_='tech-specs__section')
    tech_spec_rows = div_tech_specs_section.find_all('div', class_='tech-specs__row')

    # Get each spec_name, value pairing for bike product
    prod_specs = dict()

    try:
      for spec_row in tech_spec_rows:
        spec_name = spec_row.find('b', class_='tech-specs__name').contents[0]
        spec_value = spec_row.find('span', class_='tech-specs__value').contents[0]
        prod_specs[spec_name] = spec_value
        self._specs_fieldnames.add(spec_name)
    except AttributeError as err:
      print(f'\tError: {err}')

    print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
    return prod_specs

  def get_all_available_prods(self, to_csv=True):
    # Ensure product listings dict is empty
    self._products = dict()

    # Get initial page and determine total number of products pages to scrape
    page_soup = BeautifulSoup(self._fetch_prod_listing_view(), 'lxml')
    num_pages = self._get_num_pages(soup=page_soup)

    # Scrape first page while its in memory then fetch and scrape the remaining pages
    self._get_prods_on_current_listings_page(soup=page_soup)
    print(f'Current number of products: {len(self._products)}')

    for page_num in range(1, num_pages):
      page_soup = BeautifulSoup(self._fetch_prod_listing_view(page=page_num), 'lxml')
      self._get_prods_on_current_listings_page(soup=page_soup)   
      print(f'Current number of products: {len(self._products)}')

    if to_csv:
      self._write_prod_listings_to_csv()


if __name__ == "__main__":
  prod_file_path = os.path.join(DATA_PATH, TIMESTAMP,
    f'competitive_prod_listing_{TIMESTAMP}.csv')
  
  cc = CompetitiveCyclist()
  # cc.get_all_available_prods()
  cc.get_product_specs(get_prods_from=prod_file_path)
