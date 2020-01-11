"""
Module for scraping wiggle.com for its bike data.
"""
from math import ceil
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Wiggle(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH, page_size=96):
        """Class for scraping www.wiggle.com website.

        :param save_data_path: The base path for saving data.
        :param page_size: Number of products on page. For this site, options
            are 24, 48, and 96.
        """
        super().__init__(base_url='http://www.wiggle.com',
                         source='wiggle', save_data_path=save_data_path)
        self._page_size = page_size
        self._CYCLE_URL = f'{self._BASE_URL}/cycle/bikes'

    def _fetch_prod_listing_view(self, url, page_size=96, prod_num=1):
        req_url = f'{url}?g={prod_num}&ps={page_size}'
        # req_url = f'{self._BASE_URL}/cycle/bikes/?g={prod_num}&ps={page_size}'
        return self._fetch_html(req_url)

    def _get_categories(self) -> dict:
        """Fetch bike type categories and hrefs."""
        categories = dict()
        exclude = ['bmx_bikes', 'kids_bikes', 'view_all']

        # fetch and parse main cycles page
        soup = BeautifulSoup(
            self._fetch_prod_listing_view(url=self._CYCLE_URL, page_size=24),
            'lxml'
        )
        content_bikes = soup.find(id='content-category')
        a_tags = content_bikes.find_all('a',
                                        class_='bem-left-hand-navigation__item-link')

        # parse all hrefs
        for a in a_tags:
            href = a['href']
            bike_type = a.span.string.strip()
            bike_type, count = bike_type.split('(')
            bike_type = self._normalize_spec_fieldnames(bike_type)
            count = count.replace(')', '').strip()
            if bike_type in exclude:
                continue
            categories[bike_type] = {
                'href': href,
                'count': int(count)
            }

        return categories

    def _get_subtypes(self) -> dict:
        categories = dict()
        bike_cats = self._get_categories()
        for bike_type, values in bike_cats.items():
            href = values['href']
            subtypes = dict()
            soup = BeautifulSoup(
                self._fetch_html(url=href),
                'lxml'
            )
            content_bikes = soup.find(id='content-category')
            a_tags = content_bikes.find_all(
                'a', class_='bem-left-hand-navigation__item-link'
            )
            # handle no subtypes
            if not a_tags:
                categories[bike_type] = {
                    bike_type: {
                        'href': href,
                        'count': values['count']
                    }
                }
                continue

            # parse all hrefs
            for a in a_tags:
                subtype = a.span.string.strip()
                subtype, count = subtype.split('(')
                subtype = self._normalize_spec_fieldnames(subtype)
                count = count.replace(')', '').strip()
                subtypes[subtype] = {
                    'href': a['href'],
                    'count': int(count)
                }
            categories[bike_type] = subtypes
        return categories

    def _get_max_num_prods(self, soup):
        """Get total number of products available."""
        text_block = soup.find('div', class_='bem-paginator__text-block').string

        if text_block:
            return int(text_block.split()[-1])

        return 0  # implies no products on page

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        div_id_products = soup.find('div', attrs={'id': 'search-results'})
        div_products_list = div_id_products.find_all(
            'div', class_='js-result-list-item'
        )

        for prod_info in div_products_list:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype
            }

            # get id
            prod_id = prod_info['data-id']
            product['product_id'] = prod_id

            # get page href, description, and parse brand
            prod_a = prod_info.a
            prod_href = prod_a['href'].split('/')[3]
            product['href'] = f'/{prod_href}'
            desc = prod_a['title']
            product['description'] = desc
            product['brand'] = desc.split()[0]

            # get current and msrp price
            try:  # handle possible "TEMPORARILY OUT OF STOCK" scenario
                prod_price = prod_info.find('span',
                                            class_='bem-product-price__unit--grid')
                price = prod_price.string.split('-')[-1]
                price = float(price.strip().strip('$').replace(',', ''))
                product['price'] = price

                prod_discount = prod_info.find('span',
                                               class_='bem-product_price__discount')

                if prod_discount:
                    discount = prod_discount.string.split('-')[-1]
                    discount = float(discount.strip().split()[-1].strip('%')) / 100.0
                    product['msrp'] = round(price / (1.0 - discount), 2)
                else:
                    product['msrp'] = price
            except AttributeError:
                print("TEMPORARILY OUT OF STOCK")
                product['price'] = -1
                product['msrp'] = -1

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        # parse details/description
        # details are in two section: one near price
        # another near tech specs
        div_price_detail = soup.find('div', class_='bem-pdp__pricing')
        div_price_detail = div_price_detail.find(
            'div', attrs={'itemprop': 'description'}
        )
        details = div_price_detail.text.strip()
        div_details = soup.find(
            'div', class_='bem-pdp__product-description--written'
        )
        details += '\n' + div_details.text.strip()

        # parse tech specifications
        prod_specs = dict()
        try:
            div_product_desc_table = soup.find('div',
                                               class_='bem-pdp__product-description--tabular')
            li_feature_items = div_product_desc_table.find_all('li',
                                                               class_='bem-pdp__features-item')

            # Get each spec_name, value pairing for bike product
            for feature in li_feature_items:
                try:
                    spec_name, spec_value = feature.string.split(': ')
                    spec_name = self._normalize_spec_fieldnames(spec_name)
                    prod_specs[spec_name] = spec_value.strip()
                    self._specs_fieldnames.add(spec_name)
                except ValueError:
                    continue
            prod_specs['details'] = details
            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # get categories and fetch all products for each category
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, values in subtypes.items():
                page_url = values['href']
                num_prods = values['count']

                # get all products for bike type fetch max num of prods per page
                self._page_size = 96
                num_pages = ceil(num_prods / self._page_size)
                for i in range(num_pages):
                    print(f'\nParsing page {i + 1} for {bike_type}:{subtype}...')
                    prod_num = i * 96 + 1  # set query str for next page
                    soup = BeautifulSoup(
                        self._fetch_prod_listing_view(page_url, prod_num=prod_num,
                                                      page_size=self._page_size),
                        'lxml'
                    )
                    self._get_prods_on_current_listings_page(
                        soup, bike_type, subtype
                    )

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()
