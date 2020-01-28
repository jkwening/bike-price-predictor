"""
Module for scraping canyon.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class Canyon(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://www.canyon.com',
                         source='canyon', save_data_path=save_data_path)
        self._BIKE_MODELS_ENDPOINT = '/on/demandware.store/Sites-US-Site/en_US/Include-BikeFamilySlidersLazy?'
        self._PAGE_SIZE = 72
        self._BIKE_TYPES = ['mountain', 'road', 'urban', 'fitness']

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_bike_type_models_hrefs(self, bike_type) -> list:
        """Get list of model hrefs for bike type."""
        endpoint = self._BIKE_MODELS_ENDPOINT + 'mode=neutral&cgid=' + bike_type
        soup = BeautifulSoup(self._fetch_prod_listing_view(endpoint), 'lxml')
        a_tags = soup.find_all('a', class_='bikeModelSlider__allModels')
        hrefs = list()
        for tag in a_tags:
            hrefs.append(tag['href'])
        return hrefs

    def _get_categories(self) -> dict:
        """Fetch bike type categories and hrefs.

        Note: Canyon site has multiple bike type models hrefs.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        for bike_type in self._BIKE_TYPES:
            hrefs = self._get_bike_type_models_hrefs(bike_type)
            categories[bike_type] = {'hrefs': hrefs}
        return categories

    def _get_subtypes(self) -> dict:
        """Generate main cat, subtype, model, and hrefs mapping.

        Returns:
            dict: {main_cat: {subtypes: {model_names: href}}}
        """
        categories = dict()
        # iterate  main categories and list of model hrefs to get subtypes
        for bike_type, model_hrefs in self._get_categories().items():
            subtypes = dict()
            categories[bike_type] = subtypes
            for href in model_hrefs['hrefs']:
                tmp = href.strip('/').replace('en-us/', '')
                main_cat, subtype, model_name = tmp.split('/')
                # normalize subtype and model_name keys
                subtype = self.normalize_spec_fieldnames(subtype)
                model_name = self.normalize_spec_fieldnames(model_name)
                # get subtype dict values or add as new and return empty dict
                subtype_val_dict = subtypes.get(subtype, dict())
                # add model_name: href pair as subtype value & update subtypes
                subtype_val_dict[model_name] = href
                subtypes[subtype] = subtype_val_dict

        return categories

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        prod_grid = soup.find(id='section-product-grid')
        products = prod_grid.find_all('li', class_='productGrid__listItem')

        for prod in products:
            product = {
                'site': self._SOURCE,
                'bike_type': bike_type,
                'subtype': subtype,
                'brand': self._SOURCE
            }

            # prod id
            div_scope = prod.find('div', class_='productTile')
            prod_id = div_scope['data-pid']
            product['product_id'] = prod_id

            # prod spec href
            a_tag = div_scope.find('a', class_='productTile__link')
            product['href'] = a_tag['href'].replace(self._BASE_URL, '')

            # other prod details
            desc = div_scope.find('span', class_='productTile__productName')
            text = desc.text.replace('New', '').strip()
            product['description'] = text

            price = div_scope.find('span', class_='productTile__productPriceSale').string
            product['price'] = float(
                price.strip().replace(',', '').split('$')[1])

            try:
                msrp = div_scope.find('span', class_='productTile__productPriceOriginal').string
                product['msrp'] = float(
                    msrp.strip().replace(',', '').split('$')[1])
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _get_max_num_prods(self, soup):
        raise NotImplementedError

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
                    print(f'Parsing prods for {bike_type}:{subtype}:{model}...')
                    soup = BeautifulSoup(self._fetch_prod_listing_view(
                        endpoint=href), 'lxml')
                    try:
                        self._get_prods_on_current_listings_page(
                            soup, bike_type, subtype
                        )
                    except AttributeError:
                        print('\tERROR parsing', href)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        prod_specs = dict()
        # parse product details/description sections
        div_detail_header = soup.find('div', class_='productDetailHeader')
        div_description = div_detail_header.find('div',
                                                 class_='productDescription')
        details = ''
        for string in div_description.stripped_strings:
            details += string + '\n'
        div_detail_bottom = soup.find('div', class_='productDetail__bottom')
        div_detail_awards = div_detail_bottom.find('div',
                                                   class_='awards__spec')
        for string in div_detail_awards.stripped_strings:
            details += string + '\n'
        prod_specs['details'] = details

        # parse tech specifications
        try:
            comp_id = soup.find(id='all-components-section-panel')
            spec_li = comp_id.find_all('li', class_='allComponentsSpecItem')

            for li in spec_li:
                spec = li.find(class_='allComponentsSpecItem__title').string.strip()
                spec = self.normalize_spec_fieldnames(spec)

                # accumulate multiple values for specs
                value = ''
                values = li.find_all(class_='allComponentsSpecItem__listItem')
                for val in values:
                    value += '_' + val.string.strip()
                prod_specs[spec] = value.strip('_')
                self._specs_fieldnames.add(spec)

            print(f'[{len(prod_specs)}] Product specs: ', prod_specs)
        except AttributeError as err:
            print(f'\t\tERROR: {err}')

        return prod_specs
