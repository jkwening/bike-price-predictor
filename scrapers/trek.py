"""
Module for scraping trek.com for its bike data.
"""
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Trek(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.trekbikes.com',
                         source='trek', save_data_path=save_data_path)
        self._PROD_PAGE_ENDPOINT = '/us/en_US/bikes/c/B100/'
        self._PAGE_SIZE = 72

    def _fetch_prod_listing_view(self, endpoint, page_size=None,
                                 page=0):
        req_url = f'{self._BASE_URL}{endpoint}'

        if page_size is not None:  # add page_size query
            req_url += f'?pageSize={page_size}&page={page}'

        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        num = soup.find('p', id='results-count--product').string.strip()
        num = int(num.split()[0])
        return num

    @staticmethod
    def _next_page(soup) -> tuple:
        try:
            nav_page = soup.find('nav', class_='pagination')
            next_a = nav_page.find(id='search-page-next')
            return True, next_a['href']
        except (KeyError, AttributeError):
            return False, ''

    def _parse_categories(self, soup, exclude) -> dict:
        categories = dict()
        field_set = soup.find('fieldset', attrs={'name': 'Category'})
        div_cat = field_set.find('div', class_='facet-group__wrap')
        a_cats = div_cat.find_all('a')

        for a in a_cats:
            title = self._normalize_spec_fieldnames(a.text.strip())
            if title in exclude:
                continue
            categories[title] = a['href']
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)
        return categories

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        exclude = ['mens_bikes', 'electric_bikes',
                   'womens_bikes', 'kids_bikes',
                   'show_all', 'show_less']
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT)
        soup = BeautifulSoup(page, 'lxml')
        return self._parse_categories(soup, exclude)

    def _get_subtypes(self) -> dict:
        subtypes = dict()
        exclude = ['aluminum_mountain_bikes', 'carbon_mountain_bikes',
                   'entry_level_beginner_mountain_bikes',
                   'womens_mountain_bikes', 'kids_mountain_bikes',
                   'carbon_road_bikes', 'disc_brake_road_bikes',
                   'lightweight_road_bikes', 'aluminum_road_bikes',
                   'aero_road_bikes', 'womens_road_bikes',
                   'womens_hybrid_bikes', 'kids_hybrid_bikes',
                   'womens_commuter_bikes', 'show_all', 'show_less']
        categories = self._get_categories()
        for bike_type, href in categories.items():
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
        self._num_bikes = 0

        # Scrape pages for each available category
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, href in subtypes.items():
                print(f'Getting {bike_type}:{subtype}...')
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href, page_size=self._PAGE_SIZE), 'lxml')
                self._get_prods_on_current_listings_page(
                    soup, bike_type, subtype
                )
                next_page, href = self._next_page(soup)

                while next_page:
                    soup = BeautifulSoup(
                        self._fetch_prod_listing_view(
                            endpoint=href,
                            page_size=self._PAGE_SIZE
                        ),
                        'lxml'
                    )
                    self._get_prods_on_current_listings_page(
                        soup, bike_type, subtype
                    )
                    next_page, href = self._next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        ul_prod = soup.find('ul', class_='product-list')
        products = ul_prod.find_all('article', class_='product-tile')

        for prod in products:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'brand': self._SOURCE,
                'subtype': subtype
            }

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

    def _parse_prod_specs(self, soup) -> dict:
        """Return dictionary representation of the product's specification."""
        # parse details/description
        div_details = soup.find(id='overview')
        details = ''
        overview = div_details.find(id='datadriven-bikeProduct-productOverview')
        if overview is not None:
            details += overview.text
        features = div_details.find(id='productFeaturesSection')
        if features is not None:
            details += '\n' + features.text
        features = div_details.find(class_='productPrimaryFeaturesComponent')
        if features is not None:
            details += '\n' + features.text
        tertiary_features = div_details.find(id='trekProductSpecificationsComponent')
        if tertiary_features is not None:
            details += '\n' + tertiary_features.text

        # parse tech specifications
        try:
            # use appropriate parser per specs html DOM structure
            section = soup.find('section', id='trekProductSpecificationsComponent')
            if section is None:
                section = soup.find('section', id='trekProductSpecificationsComponentBOM')
                prod_specs = self._specs_table_parser(section)
            else:
                prod_specs = self._specs_ul_parser(section)
            # add details
            prod_specs['details'] = details
            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
            return prod_specs
        except AttributeError as err:
            print(f'\tERROR: {err}')
            return {'details': details}

    def _specs_ul_parser(self, section) -> dict:
        """Product specs parser for ul based structure."""
        prod_specs = dict()
        ul_specs = section.find('ul')
        dls = ul_specs.find_all('dl')

        for dl in dls:
            spec = dl.find('dt').string.strip()
            spec = self._normalize_spec_fieldnames(spec)
            value = dl.find('dd').string.strip()
            prod_specs[spec] = value
            self._specs_fieldnames.add(spec)
        return prod_specs

    def _specs_table_parser(self, section) -> dict:
        """Product specs parser for table based structure."""
        prod_specs = dict()
        tr_tags = section.find_all('tr')

        spec_prev = 'default'
        for tr in tr_tags:
            # hand situations where spec has multiple rows and th are empty
            # for subsequent rows
            spec = tr.find('th')
            if spec is None:
                spec = spec_prev
                value = prod_specs[spec] + '_'  # extend prev value str
            else:
                spec = spec.string.strip()
                spec = self._normalize_spec_fieldnames(spec)
                spec_prev = spec
                value = ''  # init empty value str
            value += tr.find('td').text.strip()
            prod_specs[spec] = value
            self._specs_fieldnames.add(spec)
        return prod_specs
