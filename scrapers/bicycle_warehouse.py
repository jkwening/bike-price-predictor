"""
Module for scraping bicycle_warehouse.com for its bike data.
"""
from bs4 import BeautifulSoup

from scrapers.scraper import Scraper, RAW_DATA_PATH


class BicycleWarehouse(Scraper):
    def __init__(self, save_data_path=RAW_DATA_PATH):
        super().__init__(base_url='https://bicyclewarehouse.com',
                         source='bicycle_warehouse',
                         save_data_path=save_data_path)

    def _fetch_prod_listing_view(self, endpoint):
        req_url = f'{self._BASE_URL}{endpoint}'
        return self._fetch_html(req_url)

    def _get_max_num_prods(self, soup):
        """Get max num of products on current page."""
        raise NotImplementedError

    @staticmethod
    def _get_next_page(soup):
        """Returns (success, endpoint) for next page url."""
        # nav = soup.find('nav', class_='pagination--container')
        li = soup.find('li', class_='pagination--next')

        if li is None:
            return False, ''

        return True, li.a['href']

    def _get_categories(self) -> dict:
        """Bike category endpoint encodings.

        Returns:
            dictionary of dictionaries
        """
        categories = dict()
        exclude = ['kids_bikes', 'bmx_bikes']

        page = self._fetch_prod_listing_view('')
        soup = BeautifulSoup(page, 'lxml')

        nav_cat = soup.find('nav', class_='site-navigation')
        li_bikes = nav_cat.find('li', class_='navmenu-id-bikes')
        ul_bikes = li_bikes.find('ul', class_='navmenu-depth-2')
        li_cats = ul_bikes.find_all('li', class_='navmenu-item-parent')

        for li in li_cats:
            bike_cat = dict()
            title = self._normalize_spec_fieldnames(li.a.contents[0].strip())
            if title in exclude:  # skip categories in exclude list
                continue
            bike_cat['href'] = li.a['href']
            categories[title] = bike_cat
            # print(f'[{len(categories)}] New category {title}: ', bike_cat)

        return categories

    def _get_subtypes(self) -> dict:
        """Get subtypes for each category via recommended use url."""
        categories = dict()
        exclude = ['kids_bikes', 'bmx_bikes', 'electric_bikes']

        page = self._fetch_prod_listing_view('')
        soup = BeautifulSoup(page, 'lxml')

        nav_cat = soup.find('nav', class_='site-navigation')
        li_bikes = nav_cat.find('li', class_='navmenu-id-bikes')
        ul_bikes = li_bikes.find('ul', class_='navmenu-depth-2')
        li_cats = ul_bikes.find_all('li', class_='navmenu-item-parent')

        for li in li_cats:
            # get main bike type category
            cat = li.find('a', class_='navmenu-link-parent').text.strip()
            cat = self._normalize_spec_fieldnames(cat)
            if cat in exclude:  # skip categories in exclude list
                continue

            # get all sub_types
            subtypes = dict()
            ul_sub_menu = li.find('ul', class_='navmenu-submenu')
            links = ul_sub_menu.find_all('a', class_='navmenu-link')
            for link in links:
                sub_type = self._normalize_spec_fieldnames(link.text.strip())
                if 'view_all' in sub_type:  # skip 'view all' urls
                    continue
                subtypes[sub_type] = link['href']
            categories[cat] = subtypes

        return categories

    def get_all_available_prods(self, to_csv=True) -> list:
        """Scrape bicycle_warehouse site for prods."""
        # Reset scraper related variables
        self._products = dict()
        self._num_bikes = 0

        # Scrape pages for each available category
        bike_categories = self._get_subtypes()
        for bike_type in bike_categories:
            sub_types = bike_categories[bike_type]
            for sub_type, href in sub_types.items():
                print(f'Parsing first page for {bike_type}: {sub_type}...')
                soup = BeautifulSoup(self._fetch_prod_listing_view(
                    endpoint=href), 'lxml')
                self._get_prods_on_current_listings_page(soup, bike_type,
                                                         sub_type)
                next_page, endpoint = self._get_next_page(soup)

                counter = 1
                while next_page:
                    counter += 1
                    print('\tparsing page:', counter)
                    soup = BeautifulSoup(self._fetch_prod_listing_view(
                        endpoint), 'lxml')
                    self._get_prods_on_current_listings_page(soup, bike_type,
                                                             sub_type)
                    next_page, endpoint = self._get_next_page(soup)

        if to_csv:
            return [self._write_prod_listings_to_csv()]

        return list()

    def _get_prods_on_current_listings_page(self, soup, bike_type, subtype):
        """Parse products on page."""
        products = soup.find_all(class_='productgrid--item')

        for prod in products:
            product = dict()
            product['site'] = self._SOURCE
            product['bike_type'] = bike_type
            product['subtype'] = subtype

            item = prod.find('div', class_='productitem--info')
            # Get href, description, and brand
            a_tag = item.h2.a
            product['href'] = a_tag['href']
            product['description'] = a_tag.string.strip()
            product['brand'] = product['description'].split()[0].strip()

            # Get prod id
            prod_id = item.find(class_='shopify-product-reviews-badge')['data-id']
            # prod_id = div_id['data-product-id']
            product['product_id'] = prod_id

            # Parse price
            div_price = item.find('div', class_='productitem--price')
            main_price = div_price.find('div', class_='price--main')
            price = main_price.find('span', class_='money').string
            product['price'] = float(price.strip().strip('$').replace(',', ''))

            # Parse msrp accordingly
            try:
                comp_span = div_price.find('div', class_='price--compare-at')
                msrp = comp_span.find('span', class_='money').string
                product['msrp'] = float(
                    msrp.strip().strip('$').replace(',', ''))
            except AttributeError:  # handle not on sale
                product['msrp'] = product['price']

            self._products[prod_id] = product
            print(f'[{len(self._products)}] New bike: ', product)

    def _parse_prod_specs(self, soup):
        """Return dictionary representation of the product's specification."""
        # Default: spec div tab with two or more tabs
        tabs = soup.find('div', id='tabs')

        # check for specifications tab or embedded with description
        tab = tabs.find('div', id='tabs-3')

        # prep for adding details in specs, start assume details in own tab
        details_tab_style = 'alone'
        details_tab = tabs.find('div', id='tabs-2')
        if tab is None:
            tab = tabs.find('div', id='tabs-2')
            # parse details with specs embedded in first tab
            details_tab_style = 'embedded'

        # def check for un-tabbed embedded specs
        if tab is None:
            div = soup.find('div', class_='easytabs-text')
            # note details tab setup
            details_tab_style = 'easytabs'
            details_tab = div

            # check for ul or table
            ul = div.find('ul')
            if ul is None:
                rows = div.find_all('tr')
                prod_specs = self._specs_parse_table(rows_soup=rows)
            else:
                print('[div.easy_tabs.ul]')
                prod_specs = self._specs_parse_colon_text(ul_soup=ul)
        else:
            # check for table vs string formatting
            table = tab.find('table')
            if table is None:
                prod_specs = self._specs_parse_text_format(soup=tab)
            else:
                rows = table.find_all('tr')
                # check whether multi kit table and skip storing as empty
                # bc each kit has different price and no easy way to get each price.
                try:
                    first_str = rows[0].find(['td', 'th']).text.strip().lower()
                except AttributeError:
                    first_str = rows[1].find(['td', 'th']).text.strip().lower()
                if first_str == 'kit':
                    print('\tSKIPPING: Multi Kit table...')
                    prod_specs = dict()
                else:
                    prod_specs = self._specs_parse_table(rows_soup=rows)

        # add details to specs
        if details_tab_style == 'embedded':
            top_p_tags = details_tab.find_all('p', recursive=False)
            details = ''
            for p in top_p_tags:
                details += '\n' + p.text.strip()
            details.strip()
        elif details_tab_style == 'easytabs':
            try:
                details = details_tab.find('p').text.strip()
            except AttributeError:  # no details/description
                details = ''
        else:
            details = details_tab.text.strip()
        prod_specs['details'] = details

        print(f'[{len(prod_specs)}] Product specs: ', prod_specs)

        return prod_specs

    def _specs_parse_colon_text(self, ul_soup) -> dict:
        """Specs parser helper function for dealing with colon separated specs."""
        prod_specs = dict()
        lis = ul_soup.find_all('li')
        for li in lis:
            text = li.text.strip()
            try:
                spec, value = text.split(':', 1)
            except ValueError:
                continue
            spec = spec.strip()
            spec = self._normalize_spec_fieldnames(spec)
            self._specs_fieldnames.add(spec)
            prod_specs[spec] = value.strip()

        return prod_specs

    def _specs_parse_table(self, rows_soup) -> dict:
        """Specs parser helper function for dealing with tables."""
        prod_specs = dict()
        # parse each row as spec_name:value pairs
        for tr in rows_soup:
            tds = tr.find_all(['td', 'th'])
            if not tds:  # empty table row
                continue

            if len(tds) == 1:  # handle single <td>/<th>
                text = tds[0].text.strip()
                try:
                    spec, value = text.split(':', 1)
                except ValueError:  # treat as empty value
                    spec = text
                    value = ''
                spec = spec.strip()
                spec = self._normalize_spec_fieldnames(spec)
                self._specs_fieldnames.add(spec)
                value = value.strip()
            else:
                # process child tags in batches of two as spec_name:value pairs
                for i in range(0, len(tds), 2):
                    spec = tds[i].text.strip()
                    spec = self._normalize_spec_fieldnames(spec)
                    self._specs_fieldnames.add(spec)
                    # handle empty value cell
                    try:
                        value = tds[i + 1].text.strip()
                    except IndexError:
                        value = None
            prod_specs[spec] = value
        return prod_specs

    def _specs_parse_text_format(self, soup) -> dict:
        """Specs parser helper function for dealing with text format specs."""
        prod_specs = dict()

        def p_format(p_soup):
            """Process specs text stored with <p> tag."""
            # iterate through strings mapping into spec_name:value pairs
            strings = p_soup.strings
            counter = 1
            cur_spec = ''  # track recently found spec_name
            for s in strings:
                spec = self._normalize_spec_fieldnames(s)
                if not spec:  # skip empty lines
                    continue
                # determine whether spec or value string
                if counter % 2 != 0:
                    cur_spec = spec
                    self._specs_fieldnames.add(cur_spec)
                else:
                    prod_specs[cur_spec] = s.strip()
                counter += 1

        def span_format(spans_soup: list):
            num_childs = len(spans_soup)
            counter = 0
            next_is_val = False
            while counter < num_childs:
                sp = spans_soup[counter]
                if isinstance(sp, str):  # check whether empty string
                    counter += 1
                    continue
                elif next_is_val:
                    value = spans_soup[counter].text.strip()
                    next_is_val = False
                elif sp.name == 'p':  # p tags embedded with span tags
                    try:  # skip if empty span
                        spec = sp.find('label').string.strip()
                    except AttributeError:
                        counter += 1
                        continue
                    spec = self._normalize_spec_fieldnames(spec)
                    self._specs_fieldnames.add(spec)
                    counter += 1
                    next_is_val = True
                    continue
                elif sp.name == 'span':
                    try:  # skip if empty span
                        spec = sp.find('label').string.strip()
                    except AttributeError:
                        counter += 1
                        continue
                    spec = self._normalize_spec_fieldnames(spec)
                    self._specs_fieldnames.add(spec)
                    value = sp.find('p').string.strip()
                else:
                    counter += 1
                    continue
                prod_specs[spec] = value
                counter += 1

        def ul_format(ul_soup):
            lis = ul_soup.find_all('li')
            for li in lis:
                lbl = li.find('label')
                span = li.find('span')
                strong = li.find('strong')
                value = li.text.strip()
                # handle inconsistent label tags issue
                if lbl:
                    spec = lbl.text.strip()
                    value = value.replace(spec, '')
                elif strong:
                    spec = strong.text
                    value = value.replace(spec, '')
                elif span:
                    # split on newlines and get first two strings
                    splits = value.split('\n')
                    spec = splits[0].strip()
                    value = splits[1].strip()
                else:
                    spec, value = value.split(' ', 1)
                    spec = spec.strip()
                    value = value.strip()
                # store specs data
                spec = self._normalize_spec_fieldnames(spec)
                self._specs_fieldnames.add(spec)
                prod_specs[spec] = value

        # check for spec text structure
        ul = soup.find('ul')
        p_tags = soup.find_all('p')
        if ul:
            ul_format(ul_soup=ul)
        elif len(p_tags) == 1:  # spec as text in <p>
            text = p_tags[0]
            p_format(p_soup=text)
        else:
            spans = soup.contents
            span_format(spans_soup=spans)

        return prod_specs
