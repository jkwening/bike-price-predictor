"""
Module for scraping bikedoctorwaldorf.com for its bike data.
"""
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class BikeDoctor(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH, page_size=60):
        super().__init__(base_url='https://www.bikedoctorwaldorf.com',
                         source='bike_doctor', save_data_path=save_data_path)
        self._page_size = page_size
        self._PROD_PAGE_ENDPOINT = '/product-list/bikes-1000/'

    def _fetch_prod_listing_view(self, page_size=60, qs=''):
        req_url = f'{self._BASE_URL}{self._PROD_PAGE_ENDPOINT}?maxItems=' \
                  f'{page_size}&{qs}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    @staticmethod
    def _get_next_page(soup) -> tuple:
        """Returns (success, endpoint) for next page url."""

        div = soup.find('div', class_='sePaginationWrapper')
        a_tag = div.find('a', class_='sePaginationLink',
                         attrs={'title': 'Next page'})

        if a_tag is None:
            return False, ''

        return True, a_tag['href']

    def _parse_categories_section(self, soup) -> tuple:
        """Parse categories menu section on page."""
        categories = dict()
        exclude = ['childrens', 'bmx']
        facet_cat = soup.find('div', id='Facets-categories')
        if facet_cat is None:
            return False, categories
        cats = facet_cat.find_all('li', class_='seFacet')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(c.a['title']).replace("'", "")
            if title in exclude:  # skip categories in exclude list
                continue
            bike_cat['href'] = c.a['href']
            bike_cat['filter_par'] = c.a['data-filterparameter']
            bike_cat['filter_val'] = int(c.a['data-filtervalue'])
            bike_cat['count'] = int(self._normalize_spec_fieldnames(
                c.span.contents[0]))
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)
        return True, categories

    def _get_categories(self) -> dict:
        """Get main bike categories."""

        page = self._fetch_html(url=f'{self._BASE_URL}{self._PROD_PAGE_ENDPOINT}')
        soup = BeautifulSoup(page, 'lxml')
        result, categories = self._parse_categories_section(soup)
        # main page should always have categories section raise error otherwise
        if not result:
            raise ValueError
        return categories

    def _get_subtypes(self) -> dict:
        """Get subtypes for all main categories. """
        cat_subtypes = dict()
        categories = self._get_categories()

        # get subtypes for each main category
        for bike_type in categories:
            qs = 'rb_ct=' + str(categories[bike_type]['filter_val'])
            url = f'{self._BASE_URL}{self._PROD_PAGE_ENDPOINT}?{qs}'
            soup = BeautifulSoup(self._fetch_html(url=url), 'lxml')
            result, subtypes = self._parse_categories_section(soup)
            if result:
                cat_subtypes[bike_type] = subtypes
            else:  # no subtype, store main category as it's own subtype
                cat_subtypes[bike_type] = {bike_type: categories[bike_type]}
        return cat_subtypes

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape bike_doctor site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available main category and subtype
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype in subtypes:
                qs = 'rb_ct=' + str(subtypes[subtype]['filter_val'])
                soup = BeautifulSoup(self._fetch_prod_listing_view(qs=qs),
                                     'lxml')
                print(f'Parsing first page for {bike_type}: {subtype}...')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)
                next_page, endpoint = self._get_next_page(soup)

                counter = 1
                while next_page:
                    counter += 1
                    print('\tparsing page:', counter)
                    url = f'{self._BASE_URL}{endpoint}'
                    soup = BeautifulSoup(self._fetch_html(url), 'lxml')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)
                    next_page, endpoint = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        search_products = soup.find('div', attrs={'id': 'SearchProducts'})
        products = search_products.find_all('div', class_='seProduct')
        for prod in products:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype
            }
            product_title = prod.find('div', class_='seProductTitle')

            # Get page href, product_id, and description
            href = product_title.a['href']
            product['href'] = href
            prod_id = href.split('-')[-2]
            product['product_id'] = prod_id
            item_name = product_title.a['title']

            try:  # Handle no title year
                title_year = product_title.find(
                    'span', class_='seCleanTitleYear').contents[0]
            except AttributeError:
                title_year = ''
            product['description'] = item_name + title_year

            # Get brand name
            brand_name = product_title.find('span',
                                            class_='seBrandName').contents[0]
            product['brand'] = brand_name

            # Get price
            product_price = prod.find('div', class_='seProductPrice')
            reg_price = product_price.find('span', class_='seRegularPrice')

            if reg_price is None:
                price = product_price.find(
                    'span', class_='seSpecialPrice').contents[0]
                if price.find('-') > 0:
                    price = price.split('-')[0].strip()
                msrp = product_price.find(
                    'span', class_='seOriginalPrice').contents[0]
                if msrp.find('-') > 0:
                    msrp = msrp.split('-')[0].strip()
            else:
                try:
                    price = reg_price.contents[0]
                    if price.find('-') > 0:
                        price = price.split('-')[0].strip()
                    msrp = price
                except IndexError: # No price on page
                    # TODO: Get price from product specs page
                    price = '0'
                    msrp = '0'

            product['price'] = float(price.strip('$').replace(',', ''))
            product['msrp'] = float(msrp.strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup) -> dict:
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # parse details/description section
        div_details = soup.find(id='ProductDetailsContent')
        details = div_details.find('p', attrs={'itemprop': 'description'})
        prod_specs['details'] = details.text.strip()

        # parse specifications
        try:
            id_prod_specs = soup.find('div', attrs={'id': 'ProductSpecs'})
            table_specs = id_prod_specs.find('table',
                                             class_='seProductSpecTable')
            specs = table_specs.find_all('tr')

            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = spec.th.contents[0]
                value = spec.td.contents[0]
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value.strip()
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
