import time
from datetime import datetime
import os
import math
from bs4 import BeautifulSoup
from .scraper_utils import MODULE_PATH, DATA_PATH, TIMESTAMP
from .scraper import Scraper

"""
base url = https://www.bikenashbar.com/cycling/bikes-frames#facet:&productBeginIndex:0&facetLimit:&orderBy:&pageView:grid&minPrice:&maxPrice:&pageSize:&

- pageSize: can be 24, 48, 72 items per page
- pageView: can be 'grid' or 'list'**

### products tags
div class'productListingWidget' - main div for product
div class='product_listing_container' - houses products unordered list
ul class='grid_mode ?' - ul for grid type ? = grid/list
li - lists of products
div class='product' - div container for each product following li tag
div class='product_info' - house product related info tags
div class='product_name' - has a tag which includes href and product name
a ... href='...url_for_product'>...product_name_with_year</a>

div class='title>Products:< - start of getting number products displayed
span class='num_products'>($nbsp; # - # of # $nbsp;)< - range
"""


class NashBar(Scraper):
    def __init__(self, page_size=72, page_view='list'):
        self._page_size = page_size
        self._page_view = page_view
        super().__init__(base_url='https://www.bikenashbar.com',
            prod_spec_fname='nashbar_prod_specs',
            prod_listing_fname='nashbar_prod_listing')

    def _fetch_prod_listing_view(self, product_begin_index=1, store_id=10053,
                                 catalog_id=10552, lang_id=-1,):
        req_url = 'https://www.bikenashbar.com/ProductListingView?ajaxStoreImageDir=%2F%2Fwww.bikenashbar.com%2Fwcsstore%2FAuroraStorefrontAssetStore%2F&advancedSearch=&facet=&searchTermScope=&categoryId=204647&categoryFacetHierarchyPath=&searchType=1002&filterFacet=&resultCatEntryType=&emsName=Widget_CatalogEntryList_Ext_1024819115206121167&searchTerm=&filterTerm=&resultsPerPage=24&manufacturer=&sType=SimpleSearch&disableProductCompare=false&parent_category_rn=&catalogId=10052&langId=-1&gridPosition=&ddkey=ProductListingView_6_1024819115206087258_1024819115206121167&enableSKUListView=false&storeId=10053&metaData='

        headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        data = {
            'contentBeginIndex': 0,
            'productBeginIndex': product_begin_index,
            'beginIndex': product_begin_index,
            'orderBy': 5,
            'pageView': self._page_view,
            'resultType': 'products',
            'loadProductsList': 'true',
            'storeId': store_id,
            'catalogId': catalog_id,
            'langId': lang_id,
            'homePageURL': '/cycling',
            'commandContextCurrency': 'USD',
            'urlPrefixForHTTPS': 'https://www.bikenashbar.com',
            'urlPrefixForHTTP': 'https://www.bikenashbar.com',
            'widgetPrefix': '6_1024819115206121167',
            'showColorSwatches': 'true',
            'showRatings': 'true',
            'showDiscounts': 'true',
            'pgl_widgetId': 1024819115206121167,
            'objectId': '_6_1024819115206087258_1024819115206121167',
            'requesttype': 'ajax'
        }

        print(f'begin index: {product_begin_index}')

        return self._fetch_html(url=req_url, method='POST', params=None,
                                data=data, headers=headers)

    def _get_max_num_prods(self, soup):
        self._num_bikes = super()._get_max_num_prods(soup)

    def _get_prods_on_current_listings_page(self, soup):
        """Get all bike products for the passed html page"""
        div_product_listing_widget = soup.find('div',
                                               class_='productListingWidget')
        div_product_info = div_product_listing_widget.find_all(
            'div', class_='product_info')

        for prod_info in div_product_info:
            product = dict()

            # get prod_desc, and prod_href
            div_prod_name = prod_info.find('div', class_='product_name')
            product['href'] = str(div_prod_name.a['href']).strip()
            product['desc'] = str(div_prod_name.a.string).strip()

            # get sale price (offer_price)
            span_price = prod_info.find('span', class_='price')
            product['price'] = str(span_price.string).strip()

            # get msrp price (list_price)
            span_old_price = prod_info.find('span', class_='old_price')
            if span_old_price is None:
                product['msrp'] = product['price']
            else:
                product['msrp'] = str(span_old_price.string).strip().split()[-1]

            # get prod_id
            input_info_hidden = prod_info.find('input')
            prod_id = input_info_hidden['id'].split('_')[-1]
            product['id'] = prod_id

            self._products[product['id']] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_spec = {}

        try:
            div_spec = soup.find(id='tab2Widget')

            if div_spec is None:
                error = soup.find('title')
                print(f'Error: {error.string}')
                return prod_spec

            li_specs = div_spec.ul.find_all('li')

            for spec in li_specs:
                span_name = spec.span
                span_value = span_name.find_next_sibling('span')
                name = str(span_name.string).strip().strip(':')  # get clean spec name
                name = name.strip('1')  # for some reason, some specs end with '1' for spec names
                value = str(span_value.string).strip()
                prod_spec[name] = value
                self._specs_fieldnames.add(name)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_spec

    def get_all_available_prods(self, to_csv=True):
        """Get all products currently available from site"""
        # ensure product listings dictionary is empty
        self._products = {}

        # get first product listings view page, total num bikes, total pages
        page_soup = BeautifulSoup(self._fetch_prod_listing_view(), 'lxml')
        self._get_max_num_prods(soup=page_soup)
        num_pages = math.ceil(self._num_bikes / self._page_size)
        self._get_prods_on_current_listings_page(soup=page_soup)
        print(f'Current number of products: {len(self._products)}')

        # scrape for all bikes on every product listing pages
        for page_num in range(num_pages):
            print('Page: ', page_num + 1)

            # wait 1 second then request next page
            if (page_num + 1) <= num_pages:
                time.sleep(1)
                product_begin_index = (self._page_size * page_num + 1) - 1
                page_soup = BeautifulSoup(self._fetch_prod_listing_view(
                    product_begin_index=product_begin_index), 'lxml')
                self._get_prods_on_current_listings_page(soup=page_soup)
                print(f'Current number of products: {len(self._products)}')

        if to_csv:
            self._write_prod_listings_to_csv()


if __name__ == '__main__':
    # TODO - command line options
    prod_file_path = os.path.join(DATA_PATH, TIMESTAMP,
                                 f'nashbar_prod_listing_'
                                 f'{TIMESTAMP}.csv')
    # csv_file_path = 'site'
    # csv_file_path = 'memory'

    # Fetch and save products to data folder
    pbs = NashBar()
    start = datetime.now()
    pbs.get_all_available_prods(to_csv=True)
    end = datetime.now()
    print(f'\n\nRuntime for getting all available products: {end - start}')

    specifications = pbs.get_product_specs(get_prods_from=prod_file_path,
                                           to_csv=True)

    if specifications:
        print('Success!')
