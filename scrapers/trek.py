"""
Module for scraping trek.com for its bike data.
"""
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class Trek(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://www.trekbikes.com',
                         source='trek', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/us/en_US/bikes/c/B100/'
        self._PAGE_SIZE = 72

    def _fetch_prod_listing_view(self, endpoint, page_size=None,
                                 page=0):
        req_url = f'{self._BASE_URL}{endpoint}'

        if page_size is not None:  # add page_size query
            req_url += f'?pageSize={page_size}&page={page}'

        # Spoof browser to avoid 403 error code
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'
        }
        return self._fetch_html(req_url, headers=headers)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        num = soup.find('p', id='results-count--product').string.strip()
        num = int(num.split()[0])
        return num

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        try:
            section = soup.find('section', id='trekProductSpecificationsComponent')
            ul_specs = section.find('ul')
            dls = ul_specs.find_all('dl')

            for dl in dls:
                spec = dl.find('dt').string.strip()
                spec = self._normalize_spec_fieldnames(spec)
                value = dl.find('dd').string.strip()
                prod_specs[spec] = value

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    def _get_categories(self, soup=None) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        exclude_list = ['help_me_choose', 'customize',
                        'shop_all_bikes']

        if soup is None:
            page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
            soup = BeautifulSoup(page, 'lxml')

        nav_cat = soup.find('div', attrs={'id': 'ShopByCategoryNavNode'})
        ul_cat = nav_cat.find('ul', class_='primary-navigation__links')
        a_cats = ul_cat.find_all('a')

        for a in a_cats:
            bike_cat = dict()
            bike_cat['href'] = a['href']
            title = self._normalize_spec_fieldnames(a.string.strip())
            if title in exclude_list:  # skip certain categories
                continue
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Exclude list
        exclude_list = ['womens']

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type in bike_categories.keys():
            if bike_type in exclude_list:
                continue
            print(f'Getting {bike_type}...')
            endpoint = bike_categories[bike_type]['href']
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint, page_size=self._PAGE_SIZE), 'lxml')
            self._get_prods_on_current_listings_page(soup, bike_type)
            num_bikes = self._get_max_num_prods(soup)

            if num_bikes > self._PAGE_SIZE:
                # site embeds non products on page so
                total_pages = math.ceil(num_bikes / self._PAGE_SIZE)

                for i in range(1, total_pages):
                    try:
                        soup = BeautifulSoup(self._fetch_prod_listing_view(
                            endpoint, page_size=self._PAGE_SIZE, page=i), 'lxml')
                        self._get_prods_on_current_listings_page(soup, bike_type)
                    except FileNotFoundError:
                        print(f'Page: {i} does not exist.)')
                        break  # page doesn't exist so exit

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        ul_prod = soup.find('ul', class_='product-list')
        products = ul_prod.find_all('article', class_='product-tile')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = 'trek'  # site is single brand

            try:
                prod_id = prod.find('a')['data-sku']
                product['product_id'] = prod_id
            except KeyError:  # not a product listing, skip
                continue

            a_tag = prod.find('a', id=f'product-tile-sku-price-{prod_id}')
            product['href'] = a_tag['href']
            product['description'] = a_tag['title']

            price = a_tag.find('span', class_='product-tile__saleprice').string
            try:
                product['price'] = float(
                    price.strip().strip('$').replace(',', ''))
            except ValueError:  # for ranges, take the lowest price
                low = float(price.replace(',', '').split('-')[0].strip().strip('$'))
                product['price'] = low

            try:
                msrp = a_tag.find('span', class_='product-tile__advprice').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']
            except ValueError:  # for ranges, take the lowest price
                low = float(msrp.replace(',', '').split('-')[0].strip().strip('$'))
                product['msrp'] = low

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
