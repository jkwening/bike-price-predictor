"""Module for scraping websites to collect raw data."""

from scrapers.backcountry import BackCountry
from scrapers.bike_doctor import BikeDoctor
from scrapers.bicycle_warehouse import BicycleWarehouse
from scrapers.canyon import Canyon
from scrapers.citybikes import CityBikes
from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.contebikes import ConteBikes
from scrapers.eriks import EriksBikes
from scrapers.giant import Giant
from scrapers.jenson import Jenson
from scrapers.litespeed import LiteSpeed
from scrapers.lynskey import Lynskey
from scrapers.nashbar import NashBar
from scrapers.proshop import Proshop
from scrapers.rei import Rei
from scrapers.specialized import Specialized
from scrapers.spokes import Spokes
from scrapers.trek import Trek
from scrapers.wiggle import Wiggle

from utils.utils import RAW_DATA_PATH, SOURCES, SOURCES_EXCLUDE


class Collect:
    """Handles the collection process of source data files."""

    def __init__(self, mediator, save_data_path=RAW_DATA_PATH):
        self._mediator = mediator
        self._save_data_path = save_data_path
        self._sources = SOURCES
        self._sources_exclude = SOURCES_EXCLUDE

    def _get_class_instance(self, source: str):
        """Get appropriate scraper class instance for given source."""
        if source == 'competitive':
            return CompetitiveCyclist(save_data_path=self._save_data_path)
        elif source == 'nashbar':
            return NashBar(save_data_path=self._save_data_path)
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
        elif source == 'bike_doctor':
            return BikeDoctor(save_data_path=self._save_data_path)
        elif source == 'giant':
            return Giant(save_data_path=self._save_data_path)
        elif source == 'bicycle_warehouse':
            return BicycleWarehouse(save_data_path=self._save_data_path)
        elif source == 'litespeed':
            return LiteSpeed(save_data_path=self._save_data_path)
        elif source == 'lynskey':
            return Lynskey(save_data_path=self._save_data_path)
        elif source == 'spokes':
            return Spokes(save_data_path=self._save_data_path)
        elif source == 'jenson':
            return Jenson(save_data_path=self._save_data_path)
        elif source == 'backcountry':
            return BackCountry(save_data_path=self._save_data_path)
        else:
            raise ValueError(f'Invalid source: {source} value.')

    def collect_all_products(self, get_specs=True, skip_failed=False):
        """Collect raw data file from all sources."""
        for source in self._sources:
            # skip if source in exclude list
            if source in self._sources_exclude:
                print(f'\nSKIPPING: {source} in exclude list!')
                continue

            # collect source otherwise
            try:
                self.collect_products_from_source(source, get_specs=get_specs)
            except FileNotFoundError as e:
                if not skip_failed:
                    raise FileNotFoundError(e)
                else:
                    print(f'\nSKIPPING {source}: {e}')

    def collect_from_sources(self, sources: list, get_specs=True,
                             skip_failed=False):
        """Collect raw data file from specified sources."""
        for source in sources:
            try:
                self.collect_products_from_source(source, get_specs=get_specs)
            except FileNotFoundError as e:
                if not skip_failed:
                    raise FileNotFoundError(e)
                else:
                    print(f'\nSKIPPING {source}: {e}')

    def collect_products_from_source(self, source: str, get_specs=True):
        """Collect raw data file for specified source."""
        class_ = self._get_class_instance(source)
        row_datas = class_.get_all_available_prods()
        print(f'\n{source} row_data: {row_datas}')
        self._mediator.update_manifest(rows=row_datas)
        # TODO: inspect this section - should only be single row data parsed
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
                                                 bike_type=bike_type,
                                                 to_csv=True)
        print(
            f'[collect_specs_matching] {source} spec_row_data: {spec_row_data}')
        self._mediator.update_manifest(rows=[spec_row_data])
        return spec_row_data
