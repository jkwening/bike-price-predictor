"""
Module for scraping jensonusa.com for its bike data.
"""
from bs4 import BeautifulSoup, NavigableString

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Jenson(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH, page_size=100):
        super().__init__(base_url='https://www.jensonusa.com',
                         source='jenson', save_data_path=save_data_path)
        self._page_size = page_size
        self._PROD_PAGE_ENDPOINT = '/Complete-Bikes'

    def _fetch_prod_listing_view(self, endpoint, page_size=None, page=None,
                                 include_base=True):
        if include_base:
            req_url = f'{self._BASE_URL}{endpoint}'
        else:
            req_url = endpoint
        if page_size:
            req_url += f'&pn={page}&ps={page_size}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _get_categories(self):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        # categories that should be skipped
        exlude = ['jenson_usa_exclusive_builds', 'bikes_on_sale',
                  'corona_store_exclusives', 'bmx_bikes', 'kids_bikes',
                  'electric_bikes']
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')

        div_cat = soup.find('div', class_='list-links')
        cats = div_cat.find_all('a')

        # Get all categories
        for a_tag in cats:
            title = self._normalize_spec_fieldnames(a_tag.text)
            if title in exlude:
                continue
            href = a_tag['href'].replace(self._BASE_URL, '')
            categories[title] = href
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def _get_subtypes(self) -> dict:
        categories = self._get_categories()
        bike_subtypes = dict()
        for bike_type, href in categories.items():
            page = self._fetch_prod_listing_view(endpoint=href)
            soup = BeautifulSoup(page, 'lxml')

            nav_tree = soup.find(id='navTree')
            divs = nav_tree.div.find_all('div')
            subtypes = dict()
            for div in divs:
                a_tag = div.find('a', class_='filter-leaf')
                if a_tag is None:
                    continue
                leaf_name = a_tag.text.strip()
                leaf_name = self._normalize_spec_fieldnames(leaf_name)
                if leaf_name == 'intended_use':
                    lvl1 = div.find('div', class_='filter-level1')
                    tags = lvl1.find_all('a', class_='filter-option-link')
                    for tag in tags:
                        subtype = self._normalize_spec_fieldnames(tag['title'])
                        href = tag['href']
                        subtypes[subtype] = href
            bike_subtypes[bike_type] = subtypes
        return bike_subtypes

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Populate categories if missing
        categories = self._get_subtypes()

        # Scrape pages for each available category
        for bike_type, subtypes in categories.items():
            for subtype, href in subtypes.items():
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href, include_base=False
                ), 'lxml')
                print(f'Parsing {bike_type}:{subtype}...')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)
                try:
                    pages = soup.find('span', class_='page-label').text
                    pages = int(pages.strip().split()[-1])
                except AttributeError:
                    # No next page
                    pages = 0

                # Scrape all pages for bike category
                for page in range(1, pages):
                    soup = BeautifulSoup(self._fetch_prod_listing_view(
                        endpoint=href, page=page, page_size=self._page_size,
                        include_base=False
                    ), 'lxml')
                    print(f'\t\tParsing next page...')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        try:
            section = soup.find('section', id='productList')
            container = section.find('div', class_='product-list-container')
            products = container.find_all('div', class_='item-content')
        except AttributeError:
            print('\tError: No products for', bike_type)
            return None

        for prod in products:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype
            }

            # Parse prod id
            prod_id = prod['id']
            product['product_id'] = prod_id

            # Get page href, title, description, and brand
            a_tag = prod.find('a', class_='product-name')
            product['href'] = a_tag['href']
            product['description'] = a_tag.string.strip()
            product['brand'] = product['description'].split()[0]

            # Get price
            price = prod.find('div', class_='product-price-saleprice').text.strip()
            price = price.lower().replace('from', '').strip()
            product['price'] = float(price.strip('$').replace(',', ''))

            try:
                msrp = prod.find('div', class_='product-price-defprice').string.strip()
                msrp = msrp.replace('MSRP', '').strip()
                product['msrp'] = float(msrp.strip('$').replace(',', ''))
            except AttributeError:
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        id_prod_specs = soup.find('div', id='prod-tab-frame-D')

        # parse children tags until table is reached
        # details and specs are embedded within same tab
        details = ''
        for child in id_prod_specs.children:
            if child.name == 'table':
                break

            if isinstance(child, NavigableString):
                continue

            # stripped strings for tag
            for string in child.stripped_strings:
                details += string + '\n'
        prod_specs['details'] = details

        # parse tech specs
        try:
            table_specs = id_prod_specs.find_all('table', class_='spec')
            table_spec = table_specs[0]

            # Handle multiple table specs
            if len(table_specs) > 1:
                for table in table_specs:
                    caption = table.caption.string.lower().strip()
                    if caption == 'bike specifications':
                        table_spec = table
                        break

            # Get each spec_name, value pairing for bike product
            specs = table_spec.find_all('tr')
            for spec in specs:
                name = spec.th.string
                value = spec.td.text
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value.strip()
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')
        except IndexError:
            print('f\tError: Specifications table not available!')

        return prod_specs
