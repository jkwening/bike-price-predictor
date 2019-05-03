"""Module for scraping websites to collect raw data."""

from scrapers.citybikes import CityBikes
from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.nashbar import NashBar
# from scrapers.performance_bike import PerformanceBikes
from scrapers.proshop import Proshop
from scrapers.contebikes import ConteBikes
from scrapers.eriks import EriksBikes
from scrapers.rei import Rei
from scrapers.wiggle import Wiggle
from scrapers.trek import Trek
from scrapers.specialized import Specialized
from scrapers.canyon import Canyon
from scrapers.foxvalley import FoxValley
from scrapers.giant import Giant
from scrapers.bicycle_warehouse import BicycleWarehouse

from utils.utils import DATA_PATH


class Collect:
    """Handles the collection process of source data files."""

    def __init__(self, mediator, save_data_path=DATA_PATH):
        self._mediator = mediator
        self._save_data_path = save_data_path
        self._SOURCES = [
            'competitive', 'nashbar', 'trek',
            'wiggle', 'rei', 'citybikes', 'proshop',
            'contebikes', 'eriks', 'specialized',
            'foxvalley', 'canyon', 'giant',
            'bicycyle_warehouse'
        ]

    def _get_class_instance(self, source: str):
        """Get appropriate scraper class instance for given source."""
        if source == 'competitive':
            return CompetitiveCyclist(save_data_path=self._save_data_path)
        elif source == 'nashbar':
            return NashBar(save_data_path=self._save_data_path)
        # elif source == 'performance':
        #     return PerformanceBikes(save_data_path=self._save_data_path)
        elif source == 'wiggle':
            return Wiggle(save_data_path=self._save_data_path)
        elif source == 'rei':
            return Rei(save_data_path=self._save_data_path)
        elif source == 'citybikes':
            return CityBikes(save_data_path=self._save_data_path)
        elif source == 'contebikes':
            return ConteBikes(save_data_path=self._save_data_path)
        elif source == 'proshop':
            return Proshop(save_data_path=self._save_data_path)
        elif source == 'eriks':
            return EriksBikes(save_data_path=self._save_data_path)
        elif source == 'specialized':
            return Specialized(save_data_path=self._save_data_path)
        elif source == 'trek':
            return Trek(save_data_path=self._save_data_path)
        elif source == 'canyon':
            return Canyon(save_data_path=self._save_data_path)
        elif source == 'foxvalley':
            return FoxValley(save_data_path=self._save_data_path)
        elif source == 'giant':
            return Giant(save_data_path=self._save_data_path)
        elif source == 'bicycle_warehouse':
            return BicycleWarehouse(save_data_path=self._save_data_path)
        else:
            raise ValueError(f'Invalid source: {source} value.')

    def collect_all_products(self, get_specs=True, skip_failed=False):
        """Collect raw data file from all sources."""
        for source in self._SOURCES:
            try:
                self.collect_products_from_source(source, get_specs=get_specs)
            except FileNotFoundError as e:
                if not skip_failed:
                    raise FileNotFoundError(e)
                else:
                    print(f'Skipping {source}: {e}')

    def collect_from_sources(self, sources: list, get_specs=True,
                             skip_failed=False):
        """Collect raw data file from specified sources."""
        if not sources:  # Assume all sources if empty list
            sources = self._SOURCES

        for source in sources:
            try:
                self.collect_products_from_source(source, get_specs=get_specs)
            except FileNotFoundError as e:
                if not skip_failed:
                    raise FileNotFoundError(e)
                else:
                    print(f'Skipping {source}: {e}')

    def collect_products_from_source(self, source: str, get_specs=True):
        """Collect raw data file for specified source."""
        class_ = self._get_class_instance(source)
        row_datas = class_.get_all_available_prods()
        print(f'{source} row_datas: {row_datas}')
        self._mediator.update_manifest(rows=row_datas)

        if get_specs:
            spec_rows = list()
            for row_data in row_datas:
                filepath = self._mediator.get_filepath_for_manifest_row(
                    row=row_data)
                spec_row = class_.get_product_specs(get_prods_from=filepath,
                                                    bike_type=row_data[
                                                        'bike_type'])
                spec_rows.append(spec_row)
            self._mediator.update_manifest(rows=spec_rows)

    def collect_specs_matching(self, source: str, bike_type: str) -> dict:
        """Collect specs data for given product source and bike_type."""
        row = self._mediator.get_rows_matching(sources=[source],
                                               bike_types=[bike_type],
                                               tablenames=['products'])[0]

        filepath = self._mediator.get_filepath_for_manifest_row(row)

        class_ = self._get_class_instance(source)
        spec_row_data = class_.get_product_specs(get_prods_from=filepath,
                                                 bike_type=bike_type)
        print(
            f'[collect_specs_matching] {source} spec_row_data: {spec_row_data}')
        self._mediator.update_manifest(rows=[spec_row_data])
        return spec_row_data
