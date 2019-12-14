"""
Module for scraping bicycle_warehouse.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper
from scrapers.scraper_utils import DATA_PATH


class BicycleWarehouse(Scraper):
    def __init__(self, save_data_path=DATA_PATH):
        super().__init__(base_url='https://bicyclewarehouse.com',
                         source='bicycle_warehouse',
                         save_data_path=save_data_path)

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

    @staticmethod
    def _get_next_page(soup):
        """Returns (success, endpoint) for next page url."""
        # nav = soup.find('nav', class_='pagination--container')
        li = soup.find('li', class_='pagination--next')

        if li is None:
            return False, ''

        return True, li.a['href']

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # Default: spec div tab with two or more columns
        div_tab = soup.find('div', id='tabs-3')

        if div_tab is not None:  # move to next tab if not specs tab
            # frame = 'frame' not in div_tab.text.lower()
            fork = 'fork' not in div_tab.text.lower()
            if fork:
                div_tab = soup.find('div', id='tabs-4')
        section = div_tab
        split_on_colon = False
        if div_tab is None:
            div_desc = soup.find('div', class_='product-description')
            section = div_desc

        # Check if stored in table format
        table = section.find('table', class_='table-striped')
        if table is None:  # handle list format scenario
            ul = section.find('ul')
            if ul is not None:  # ensure ul and not just structured text
                section = ul
                split_on_colon = True
        else:  # handle table format scenario, factoring into number of cols
            try:
                section = table
                cols = section.find('tr').find_all(['th', 'td'])
                split_on_colon = True if len(cols) == 1 else False
            except AttributeError as err:
                print(f'\tError: {err}')

        try:
            cur_spec = ''
            count = 1
            for string in section.strings:
                s_ = self._normalize_spec_fieldnames(string)
                if not s_:  # skip empty lines
                    continue

                if split_on_colon:  # handle single column or bullets specs data
                    try:
                        spec, value = string.split(':', 1)
                    except ValueError:  # skip if single column or bullets but no fields
                        print('\tError: skipping...')
                        break
                    spec = self._normalize_spec_fieldnames(spec)
                    self._specs_fieldnames.add(spec)
                    prod_specs[spec] = value.strip()
                    # print(f'{count}: {spec} - {value.strip()}')
                else:
                    if count % 2 != 0:
                        cur_spec = s_
                        self._specs_fieldnames.add(cur_spec)
                        # print(f'{count}: {cur_spec}')
                    else:
                        prod_specs[cur_spec] = string.strip()
                        # print(f'{count}: {cur_spec} - {string.strip()}')

                count += 1

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
        exclude = ['kids_bikes']

        if soup is None:
            page = self._fetch_prod_listing_view('')
            soup = BeautifulSoup(page, 'lxml')

        nav_cat = soup.find('nav', class_='site-navigation')
        li_bikes = nav_cat.find('li', class_='navmenu-id-bikes')
        ul_bikes = li_bikes.find('ul', class_='navmenu-depth-2')
        li_cats = ul_bikes.find_all('li', class_='navmenu-item-parent')

        for li in li_cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(li.a.contents[0].strip())
            if title in exclude:  # skip categories in exclude list
                continue
            bike_cat['href'] = li.a['href']
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_categories()
        for bike_type in bike_categories:
            print(f'Parsing first page for {bike_type}...')
            endpoint = bike_categories[bike_type]['href']
            soup = BeautifulSoup(self._fetch_prod_listing_view(
                endpoint), 'lxml')
            self._get_prods_on_current_listings_page(soup, bike_type)
            next_page, endpoint = self._get_next_page(soup)

            counter = 1
            while next_page:
                counter += 1
                print('\tparsing page:', counter)
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)
                next_page, endpoint = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type):
        """Parse products on page."""
        products = soup.find_all(class_='productgrid--item')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type

            item = prod.find('div', class_='productitem--info')
            # Get href, description, and brand
            a_tag = item.h2.a
            product['href'] = a_tag['href']
            product['description'] = a_tag.string.strip()
            product['brand'] = product['description'].split()[0].strip()

            # Get prod id
            prod_id = item.find(class_='shopify-product-reviews-badge')['data-id']
            # prod_id = div_id['data-product-id']
            product['product_id'] = prod_id

            # Parse price
            div_price = item.find('div', class_='productitem--price')
            main_price = div_price.find('div', class_='price--main')
            price = main_price.find('span', class_='money').string
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                comp_span = div_price.find('div', class_='price--compare-at')
                msrp = comp_span.find('span', class_='money').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)
