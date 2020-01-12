"""
Module for scraping backcountry.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class BackCountry(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.backcountry.com',
                         source='backcountry',
                         save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/bikes-frames'

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup) -> int:
        """Get max num of products on 'PROD_PAGE_ENDPOINT'."""
        span = soup.find('span', class_='plp-toolbar__results-quantity js-results-qty')
        num_prods = int(span.string.strip().split()[0])
        return num_prods

    @staticmethod
    def _get_next_page(soup):
        """Returns (success, endpoint) for next page url."""
        li = soup.find('li', class_='pag-next')

        if li is None:
            return False, ''

        return True, li.a['href']

    def _parse_categories(self, soup, exclude) -> dict:
        categories = dict()
        div_facet = soup.find('div', id='facet-Categories')
        div_items = div_facet.find('div', id='category-filter-list')
        input_cats = div_items.find_all('input')

        for tag in input_cats:
            title = self._normalize_spec_fieldnames(tag['title'])
            if title in exclude:  # skip categories in exclude list
                continue
            categories[title] = tag['data-filter-url']
        return categories

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        exclude = ['kids_bikes']

        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')
        categories = self._parse_categories(soup, exclude)

        return categories

    def _get_subtypes(self) -> dict:
        """Get subtypes for each category via recommended use url."""
        subtypes = dict()
        exclude = ['road_frames', 'gravel_cyclocross_frames',
                   'triathlon_tt_frames']
        bike_cats = self._get_categories()
        for bike_type, href in bike_cats.items():
            soup = BeautifulSoup(
                self._fetch_prod_listing_view(endpoint=href),
                'lxml'
            )
            subtypes[bike_type] = self._parse_categories(soup, exclude)
        return subtypes

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = self._get_max_num_prods(
            BeautifulSoup(self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT),
                          'lxml')
        )

        # Scrape pages for each available category and respective subtype
        bike_categories = self._get_subtypes()
        for bike_type, subtypes in bike_categories.items():
            for subtype, href in subtypes.items():
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href), 'lxml')
                print(f'Parsing first page for {bike_type}: {subtype}...')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)
                next_page, endpoint = self._get_next_page(soup)

                counter = 1
                while next_page:
                    counter += 1
                    print('\tparsing page:', counter)
                    soup = BeautifulSoup(self._fetch_prod_listing_view(
                        endpoint), 'lxml')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)
                    next_page, endpoint = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        grid = soup.find('div', class_='plp-product-grid')
        products = grid.find_all('div', class_='product')

        for prod in products:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype
            }

            # Get prod id
            prod_id = prod['data-product-id']
            product['product_id'] = prod_id

            # Get href, description, and brand
            a_tag = prod.div.a
            product['href'] = a_tag['href']
            div_name = a_tag.find('div', class_='ui-pl-name')
            product['brand'] = div_name.find('span', class_='ui-pl-name-brand').string.strip()
            desc = div_name.find('span', class_='ui-pl-name-title').string.strip()
            product['description'] = f'{product["brand"]} {desc}'

            # Parse price
            div_price = a_tag.find('div', class_='ui-pl-offers')
            span_price = div_price.find('span', class_='retail')

            if span_price:
                price = div_price.find('span', class_='price-retail').string
                product['price'] = float(price.strip().strip('$').replace(',', ''))
                product['msrp'] = product['price']
            else:
                price = div_price.find('span', class_='ui-pl-pricing-low-price').string
                product['price'] = float(price.strip().strip('$').replace(',', ''))
                msrp = div_price.find('span', class_='ui-pl-pricing-high-price').string
                product['msrp'] = float(msrp.strip().strip('$').replace(',', ''))

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup) -> dict:
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # Specifications and details data is hidden with accordion DOM
        section = soup.find('div', id='accordion-parent')
        # parse specifications
        div_tech_specs = section.find(
            'div',
            class_='table product-details-accordion__techspecs-container'
        )
        rows = div_tech_specs.find_all('div', class_='tr')
        for row in rows:
            spec = self._normalize_spec_fieldnames(row.find(
                'div', class_='product-details-accordion__techspec-name').string)
            value = row.find('div',
                             class_='product-details-accordion__techspec-value'
                             ).string.strip()
            self._specs_fieldnames.add(spec)
            prod_specs[spec] = value

        # parse product details/description
        div_details = section.find(id='js-buybox-details-section')
        details = ''
        for string in div_details.stripped_strings:
            details += string + '\n'
        div_details_list = section.find(id='js-bulletpoints-section')
        for string in div_details_list.stripped_strings:
            details += string + '\n'
        prod_specs['details'] = details.strip()

        print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        return prod_specs
