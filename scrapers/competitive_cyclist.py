from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class CompetitiveCyclist(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH, page_size=42):
        self._page_size = page_size
        super().__init__(base_url='https://www.competitivecyclist.com',
                         source='competitive', save_data_path=save_data_path)

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_categories(self) -> dict:
        """Get bike type categories and hrefs."""
        categories = dict()
        exclude = ['sale', 'kids']

        # fetch and identify categories a tags
        soup = BeautifulSoup(
            self._fetch_html(url=self._BASE_URL),
            'lxml'
        )
        nav = soup.find('nav', class_='header-nav')
        bikes_li = nav.find('li', attrs={'data-title': 'Bikes'})
        nav = bikes_li.find('nav')
        nav_a = nav.find_all('a')

        # parse bike types and hrefs
        for a in nav_a:
            href = a['href']
            bike_type = a.string.strip()
            bike_type = self._normalize_spec_fieldnames(bike_type)
            if bike_type in exclude:
                continue
            categories[bike_type] = href
        return categories

    def _get_subtypes(self) -> dict:
        categories = self._get_categories()
        subtypes = dict()
        for bike_type, href in categories.items():
            tmp_dict = dict()
            soup = BeautifulSoup(
                self._fetch_prod_listing_view(endpoint=href),
                'lxml'
            )
            div_recommended_use = soup.find(
                id='attr_recommendeduse-filter-list'
            )
            try:
                a_tags = div_recommended_use.find_all('a')
            except AttributeError:
                tmp_dict[bike_type] = href
                subtypes[bike_type] = tmp_dict
                continue

            for a_tag in a_tags:
                subtype = a_tag['title']
                subtype = self._normalize_spec_fieldnames(subtype)
                href = a_tag['href']
                tmp_dict[subtype] = href
            subtypes[bike_type] = tmp_dict
        return subtypes

    @staticmethod
    def _get_next_page(soup) -> tuple:
        """Return (bool, href) regarding if next page button exists."""
        li = soup.find('li', class_='pag-next')

        if li is None:
            return False, ''
        else:
            href = li.a['href']
            return True, href

    def _get_max_num_prods(self, soup):
        """Get number of pages instead since number of products not easily presented."""
        pass

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        div_id_products = soup.find('div', class_='results')
        div_products_list = div_id_products.find_all('div', class_='product')

        for prod_info in div_products_list:
            product = dict()
            product['bike_type'] = bike_type
            product['site'] = self._SOURCE
            product['subtype'] = subtype

            # get id
            prod_id = prod_info['data-product-id']
            product['product_id'] = prod_id

            # get page href
            prod_href = prod_info.a['href']
            product['href'] = prod_href

            # get brand
            prod_brand = \
                prod_info.find('span', class_='ui-pl-name-brand').contents[0]
            product['brand'] = prod_brand

            # get desc
            prod_desc = \
                prod_info.find('span', class_='ui-pl-name-title').contents[0]
            product['description'] = prod_desc

            # get current and msrp price
            try:  # handle possible "TEMPORARILY OUT OF STOCK" scenario
                high_price = prod_info.find('span', class_='js-item-price-high')
                prod_msrp = high_price.contents[0]

                low_price = prod_info.find('span', class_='js-item-price-low')
                if low_price is not None:
                    prod_price = low_price.contents[0]
                else:
                    prod_price = prod_msrp

                product['price'] = float(prod_price.strip('$').replace(',', ''))
                product['msrp'] = float(prod_msrp.strip('$').replace(',', ''))
            except AttributeError:
                print("TEMPORARILY OUT OF STOCK")
                product['price'] = -1
                product['msrp'] = -1

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        # parse details/description
        div_details = soup.find(id='product-description')
        details = div_details.text.strip()
        prod_specs['details'] = details

        # parse tech specifications
        try:
            div_tech_specs_section = soup.find('div',
                                               class_='tech-specs__section')
            tech_spec_rows = div_tech_specs_section.find_all('div',
                                                             class_='tech-specs__row')

            # Get each spec_name, value pairing for bike product
            for spec_row in tech_spec_rows:
                spec_name = \
                    spec_row.find('b', class_='tech-specs__name').contents[0]
                spec_name = self._normalize_spec_fieldnames(spec_name)
                spec_value = \
                    spec_row.find('span', class_='tech-specs__value').contents[
                        0]
                prod_specs[spec_name] = spec_value
                self._specs_fieldnames.add(spec_name)
        except AttributeError as err:
            print(f'\tError: {err}')

        print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        return prod_specs

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape competitive cyclist site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, href in subtypes.items():
                print(f'Parsing first page for {bike_type}:{subtype}...')
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type)
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
