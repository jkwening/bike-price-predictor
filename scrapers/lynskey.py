"""
Module for scraping lynskeyperformance.com for its bike data.
"""
from bs4 import BeautifulSoup, NavigableString

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Lynskey(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://lynskeyperformance.com',
                         source='lynskey',
                         save_data_path=save_data_path)
        self._CATEGORIES = {
            'road': '/road-bikes/',
            'gravel': '/road/gravel',
            'mountain': '/mountain-bikes/'
        }

    def _fetch_prod_listing_view(self, endpoint, base_url=True):
        if base_url:
            req_url = f'{self._BASE_URL}{endpoint}'
        else:
            req_url = endpoint
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

    def _get_subtypes(self) -> dict:
        """Get categories and subtypes."""
        categories = dict()
        html = self._fetch_prod_listing_view(endpoint='')
        soup = BeautifulSoup(html, 'lxml')
        nav = soup.find('nav', class_='navigation')
        nav_menu1 = nav.find('ul', class_='nav-menu')
        drop_downs = nav_menu1.find_all('li', class_='has-dropdown',
                                       recursive=False)

        for drop_down in drop_downs:
            bike_type = drop_down.a.text.strip()
            bike_type = self._normalize_spec_fieldnames(bike_type)
            if bike_type in ['clearance', 'parts']:
                continue
            nav_menu2 = drop_down.find('ul', class_='nav-submenu')
            sub_menus = nav_menu2.find_all('li', class_='nav-submenu-item',
                                           recursive=False)
            subtypes = dict()
            for sub_menu in sub_menus:
                models = dict()
                subtype = sub_menu.a.text.strip()
                subtype = self._normalize_spec_fieldnames(subtype)
                if 'all' in subtype:
                    continue
                nav_menu3 = sub_menu.find('ul', class_='nav-submenu')
                # not all subtypes have sub_models, map model data to subtype
                if nav_menu3 is None:
                    models[subtype] = sub_menu.a['href']
                else:
                    # map subtype to model and respective href
                    items = sub_menu.find_all('li', class_='nav-submenu-item')
                    for item in items:
                        model = item.a.text.strip()
                        model = self._normalize_spec_fieldnames(model)
                        if 'all' in model:
                            continue
                        models[model] = item.a['href']
                subtypes[subtype] = models
            categories[bike_type] = subtypes
        return categories

    @staticmethod
    def _get_next_page(soup):
        """Get next page URL if available.

        If page has 'next' button/a tag, then return True, 'URL' tuple. Where
        'URL' is link for the next page.

        Returns False, "" otherwise.
        """
        a_tag = soup.find('a', class_='next')

        if a_tag is None:
            return False, ''

        return True, a_tag['href']

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape wiggle site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        categories = self._get_subtypes()
        for bike_type, subtypes in categories.items():
            for subtype, models in subtypes.items():
                for model, href in models.items():
                    soup = BeautifulSoup(self._fetch_prod_listing_view(
                        endpoint=href, base_url=False), 'lxml')
                    print(f'Parsing {bike_type}:{subtype}...')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             subtype)
                    next_page, url = self._get_next_page(soup)

                    # Iterate through all next pages
                    while next_page:
                        soup = BeautifulSoup(self._fetch_html(url), 'lxml')
                        print(f'\t\tParsing next page...')
                        self._get_prods_on_current_listings_page(soup, bike_type,
                                                                 subtype)
                        next_page, url = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        product = dict()
        products = soup.find_all('article', class_='product-grid-item')
        for prod in products:
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['brand'] = self._SOURCE
            product['subtype'] = subtype

            # Get product details section and title
            div_details = prod.find('div', class_='product-grid-item-details')
            a_tag = div_details.find('h3', class_='product-item-title').a
            product['href'] = a_tag['href']
            title = a_tag['title']
            product['description'] = title.strip()

            # Parse prod id
            span_id = prod.find('span', class_='quick-shop-trigger')
            prod_id = span_id['data-quick-shop-trigger']
            product['product_id'] = prod_id

            # Parse price
            price = div_details.find('span', class_='price-value').string
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                was_price = div_details.find('span', class_='price-ns')
                msrp = was_price.find('span', class_='money').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup) -> list:
        """Returns list of dictionary representation of the product's specification."""
        self._specs_fieldnames.add('frame_material')
        self._specs_fieldnames.add('upgrade_options')
        self._specs_fieldnames.add('bike_subtype')
        # parse upgrade options
        upgrade_options = dict()
        right_side = soup.find('div', class_='single-product-right')
        form = right_side.find('div', class_='single-product-form')
        div_options = form.find('div', class_='product-options')
        # upgrade options organized in two different styles
        prod_list = div_options.find_all('div', attrs={
            'data-product-attribute': 'product-list'
        })
        for prod in prod_list:
            title = prod.find(class_='form-field-title').text.strip()
            title = title.replace('Select Your', '').strip()
            title = self._normalize_spec_fieldnames(title)
            opt_list = list()
            items = prod.find_all('label', class_='product-picklist-item')
            for item in items:
                text = item.text.strip()
                opt_list.append(text)
            upgrade_options[title] = opt_list

        prod_set = div_options.find_all('div', attrs={
            'data-product-attribute': 'set-select'
        })
        for prod in prod_set:
            title = prod.find(class_='form-field-title').text.strip()
            title = title.replace('Select Your', '').strip()
            title = self._normalize_spec_fieldnames(title)
            opt_list = list()
            items = prod.find_all('option')
            for item in items:
                text = item.text.strip()
                opt_list.append(text)
            upgrade_options[title] = opt_list

        # parse details/description
        left_side = soup.find('div', class_='single-product-left')
        div_details = left_side.find(id='product-details')
        details = ''
        for child in div_details.children:
            if child.name == 'div' and child['class'] == 'tabs':
                break
            if isinstance(child, NavigableString):
                continue
            details += child.text.strip() + '\n'

        # parse tech specifications for each component option
        prod_specs = list()
        try:
            div_tabs = div_details.find('div', class_='tabs')
            div_specs = div_tabs.find_all('div', class_='tab')
            prods = {'frame_material': 'titanium'}
            for tab in div_specs:
                label = tab.find('label', class_='tab-label')
                label = self._normalize_spec_fieldnames(label.text.strip())

                rows = tab.find_all('tr')
                for row in rows:
                    tds = row.find_all('td')
                    spec = tds[0].text.strip()
                    spec = self._normalize_spec_fieldnames(spec)
                    self._specs_fieldnames.add(spec)
                    value = tds[1].text.strip()
                    prods[spec] = value
                prods['details'] = details
                prods['upgrade_options'] = upgrade_options
                prods['bike_subtype'] = label
                prod_specs.append(prods)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\tError: {err}')

        return prod_specs
