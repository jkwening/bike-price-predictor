"""
Module for scraping litespeed.com for its bike data.
"""
import json
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class LiteSpeed(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://litespeed.com',
                         source='litespeed',
                         save_data_path=save_data_path)
        self._ALL_BIKES_ENDPOINT = '/collections/shop-all-bikes'
        self._CATEGORIES = {
            'road': '/collections/titanium-road-bikes',
            'gravel': '/collections/titanium-gravel-bikes',
            'mountain': '/collections/titanium-mountain-bikes'
        }

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _fetch_prod_options(self, prod_id) -> dict:
        """Fetch product upgrade options."""
        url = f'https://option.boldapps.net/v2/litespeed-bicycles.myshopify.com' \
              f'/generate_option/{prod_id}?tmp=1578418512'
        result = json.loads(self._fetch_html(url))
        option_set = result['option_product']['option_sets'][0]
        name = option_set['internal_name']
        options = option_set['options']

        # parse upgrade option and value pairs
        upgrade = dict()
        for opt in options:
            option = opt['public_name']
            values = {'type': opt['internal_name']}
            for val_dict in opt['options_values']:
                prod = val_dict['value']
                values[prod] = float(val_dict['price_dec'])
            upgrade[option] = values

        return {
            'name': name,
            'options': upgrade
        }

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

    def _get_subtypes(self) -> dict:
        categories = dict()
        exclude = ['frames', 'all', 'frames_framesets']
        soup = BeautifulSoup(self._fetch_prod_listing_view(
            endpoint=self._ALL_BIKES_ENDPOINT
        ), 'lxml')
        sidebar = soup.find('div', class_='sidebar')
        blocks = sidebar.find_all('div', class_='sidebar-block')
        for block in blocks:
            bike_type = block.h4.text.strip()
            bike_type = self._normalize_spec_fieldnames(bike_type)
            if bike_type in exclude:
                continue
            lis = block.ul.find_all('li')
            subtypes = dict()
            for li in lis:
                subtype = li.a.string.strip()
                subtype = self._normalize_spec_fieldnames(subtype)
                if subtype in exclude:
                    continue
                subtypes[subtype] = li.a['href']
            categories[bike_type] = subtypes
        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, href in subtypes.items():
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    href), 'lxml')
                print(f'Parsing {bike_type}...')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         subtype)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type,
                                            subtype):
        """Parse products on page."""
        info = soup.find_all('a', class_='product-info__caption')

        for prod in info:
            product = {
                'site': self._SOURCE, 'bike_type': bike_type,
                'subtype': subtype, 'brand': self._SOURCE,
                'href': prod['href']
            }

            # Get product details section and title
            div_details = prod.find('div', class_='product-details')
            title = div_details.find('span', class_='title').string
            product['description'] = title.strip()

            # Generate prod id
            prod_id = self._normalize_spec_fieldnames(title)
            product['product_id'] = prod_id

            # Parse price
            price = div_details.find('span', class_='money').string.replace('USD', '')
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                was_price = div_details.find('span', class_='was_price')
                msrp = was_price.find('span', class_='money').string.replace('USD', '')
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup) -> list:
        """Returns list of dictionary representation of the product's specification."""
        prod_specs = list()

        # parse details/description
        item_prop = soup.find('div', class_='description',
                              attrs={'itemprop': 'description'})
        div_alpha = item_prop.find('div', class_='alpha')
        details = div_alpha.text.strip()
        div_omega = item_prop.find('div', class_='omega')
        details += '\n' + div_omega.text.strip()

        # get upgrade options and prices
        prod_id = soup.find('div', class_='product_form')
        prod_id = prod_id['data-product-id']
        upgrades = self._fetch_prod_options(prod_id)

        # parse tech specs
        self._specs_fieldnames.add('bike_subtype')
        self._specs_fieldnames.add('upgrade_options')
        try:
            li_sect = soup.find('li', id='tab2')
            sub_name = ''
            sub_specs = dict()
            count = 0  # Track number of tables parsed for each section
            for child in li_sect.children:
                if child.name == 'h4':
                    sub_name = child.string.strip()
                    sub_specs = dict()
                    continue

                if child.name == 'div':
                    rows = child.find_all('tr')
                    for row in rows:
                        tds = row.find_all('td')
                        # Parse spec field names
                        spec = tds[0].text.strip()
                        spec = self._normalize_spec_fieldnames(spec)
                        # Parse spec value
                        value = tds[1].string
                        if value is None:
                            continue
                        sub_specs[spec] = value.strip()
                        self._specs_fieldnames.add(spec)

                    count += 1

                if count % 2 == 0 and count > 0:
                    sub_specs['bike_subtype'] = sub_name  # sub-type as field name
                    sub_specs['details'] = details  # add details as field name
                    sub_specs['upgrade_options'] = upgrades['options']  # add upgrades options
                    prod_specs.append(sub_specs)
                    count = 0  # reset count

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
