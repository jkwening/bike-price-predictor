"""
Module for scraping ericksbikeshop.com for its bike data.
"""
import math

from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class EriksBikes(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.eriksbikeshop.com',
                         source='eriks', save_data_path=save_data_path)
        self._page_size = 30  # can't control via fetch
        self._PROD_PAGE_ENDPOINT = '/eriks-bicycle-buying-guide.aspx'

    def _fetch_prod_listing_view(self, endpoint, page=1,
                                 guide=False):
        if guide:  # Get bikes guide page
            req_url = f'{self._BASE_URL}{endpoint}'
        else:
            req_url = f'{self._BASE_URL}{endpoint}?page={page}'
        return self._fetch_html(req_url)

    # TODO: seems unnecessary, remove and embed directly into get_all_available_prods()
    def _get_max_num_prods(self, soup):
        """Raise error: Not implemented in this module."""
        raise NotImplemented

    def _get_categories(self):
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        exclude = ['youth_bikes', 'bmx_bikes', 'electric_bikes']
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT,
                                             guide=True)
        soup = BeautifulSoup(page, 'lxml')

        bucket_cont = soup.find('div', class_='GBucketCont')
        cats = bucket_cont.find_all('div', class_='GBucket')

        # Get all categories
        for c in cats:
            bike_cat = dict()
            h2 = c.h2.contents[0].replace('& ', '')
            title = self._normalize_spec_fieldnames(h2)
            if title in exclude:
                continue

            # Get href link
            bucket_links = c.find('div', class_='GBucketLinks')
            span = bucket_links.find('span')
            bike_cat['href'] = span.a['href']
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def _get_subtypes(self) -> dict:
        categories = dict()
        exclude = ['bmx', 'electric', 'kids', 'specialty',
                   'closeout_used']
        page = self._fetch_prod_listing_view(self._PROD_PAGE_ENDPOINT,
                                             guide=True)
        soup = BeautifulSoup(page, 'lxml')
        menu = soup.find(id='mymenu')
        bikes_li = menu.find('li', class_='level-0-1')
        lvl1_lis = bikes_li.find_all('li', class_='level-1')

        for lvl1 in lvl1_lis:
            bike_type = lvl1.a.string.strip()
            bike_type = self._normalize_spec_fieldnames(bike_type)
            if bike_type in exclude:
                continue

            # parse subtypes
            subtypes = dict()
            lvl2_lis = lvl1.find_all('li', class_='level-2')
            for lvl2 in lvl2_lis:
                subtype = lvl2.a.string.strip()
                subtype = self._normalize_spec_fieldnames(subtype)
                if 'buying_guide' in subtype:  # ignore 'buying guide' links
                    continue
                href = lvl2.a['href']
                subtypes[subtype] = href
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
                print(f'Getting {bike_type}:{subtype}...')
                # Scrape first page, get num bikes, and determine num pages
                soup = BeautifulSoup(self._fetch_html(url=href), 'lxml')
                num_bikes = self._get_prods_on_current_listings_page(
                    soup, bike_type, subtype, get_num_bikes=True
                )
                pages = math.ceil(num_bikes / self._page_size)

                # Scrape remaining pages for bike category
                for page in range(2, pages):
                    qs = {'\tparsing page': page}
                    soup = BeautifulSoup(self._fetch_html(
                        url=href, params=qs), 'lxml')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type,
                                            subtype,
                                            get_num_bikes=False):
        """Parse products on page."""
        search_products = soup.find('div', class_='SearchProductList')
        products = search_products.find_all('div', attrs={'id': 'Td2'})
        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['subtype'] = subtype

            dept_prod_text = prod.find('div', class_='DeptProdText')

            # Get page href, product_id, and description
            product['href'] = dept_prod_text.a['href']  # full url
            prod_id = dept_prod_text.a['rapi']
            product['product_id'] = prod_id
            desc = dept_prod_text.a.span.contents[0]
            product['description'] = desc

            # Get brand name
            product['brand'] = desc.split()[0]

            # Get price
            price = dept_prod_text.find(
                'span', class_='SalePriceA').span.contents[0]
            try:
                product['price'] = float(
                    price.strip().strip('$').replace(',', ''))
            except ValueError:
                low, high = price.split('-')
                low = float(low.strip().strip('$').replace(',', ''))
                high = float(high.strip().strip('$').replace(',', ''))
                price = (low + high) / 2  # Use average of the price ranges

            try:
                msrp = dept_prod_text.find(
                    'span', class_='MSRPPriceA').contents[0]
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

        # If requested return number of bike products
        if get_num_bikes:
            heading_info = soup.find('div', class_='searchHeadingInfo')
            results = heading_info.span.span.contents[0].split()[0]
            return int(results)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()

        # parse details/description
        div_description = soup.find('div', class_='product-description')
        feat = div_description.find('div', class_='feat')
        details = ''
        for string in feat.stripped_strings:
            details = string + '\n'
        prod_specs['details'] = details

        # parse tech specifications
        try:
            # div_feat = soup.find('div', class_='feat')
            gspecs_div = soup.find('div', class_='specs')
            table_specs = gspecs_div.find('table')
            specs = table_specs.find_all('tr')

            # Get each spec_name, value pairing for bike product
            for spec in specs:
                name = ''
                for str in spec.th.stripped_strings:
                    name += str
                value = ''
                for str in spec.td.stripped_strings:
                    value += str
                spec_name = self._normalize_spec_fieldnames(name)
                prod_specs[spec_name] = value
                self._specs_fieldnames.add(spec_name)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
