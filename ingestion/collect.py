"""Module for scraping websites to collect raw data."""

import os

from utils.utils import DATA_PATH
from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.nashbar import NashBar
from scrapers.performance_bike import PerformanceBikes


class Collect:
  """Handles the collection process of source data files."""
  def __init__(self, mediator, save_data_path=DATA_PATH):
    self._mediator = mediator
    self._save_data_path = save_data_path
    self._SOURCES = ['competitive', 'nashbar', 'performance']

  def _get_class_instance(self, source: str):
    """Get appropriate scraper class instance for given source."""
    if source == 'competitive':
      return CompetitiveCyclist(save_data_path=self._save_data_path)
    elif source == 'nashbar':
      return NashBar(save_data_path=self._save_data_path)
    elif source == 'performance':
      return PerformanceBikes(save_data_path=self._save_data_path)
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

  def collect_from_sources(self, sources: list, get_specs=True, skip_failed=False):
    """Collect raw data file from specified sources."""
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

    #FIXME: row_data = list of dict, so iterate through and get each prod filepath to get specs for
    if get_specs:
      spec_rows = list()
      for row_data in row_datas:
        filepath = self._mediator.get_filepath_for_manifest_row(row=row_data)
        spec_row = class_.get_product_specs(get_prods_from=filepath,
          bike_type=row_data['bike_type'])
        spec_rows.append(spec_row)
      self._mediator.update_manifest(rows=spec_rows)

  #FIXME: think through how to handle multiple competitive sources
  # def collect_all_specs(self,to_csv=True):
  #   manifest = Manifest()
  #   for source in self._SOURCES:
  #     self.collect_specs_for_source(source, manifest=manifest, to_csv=to_csv)

  # #FIXME: think through how to handle multiple competitive sources
  # def collect_specs_for_source(self,source, manifest=None, to_csv=True):
  #   """Get specs for ..."""
  #   if manifest is None:
  #     manifest = Manifest()
    
  #   source_prod_row = None
  #   for row in manifest.get_product_rows():
  #     if row['source'] == source:
  #       source_prod_row = row
  #       break

  #   if source_prod_row is None:
  #     raise ValueError(f'{source} does not have products row in manifest!')
    
  #   filepath = os.path.join(DATA_PATH, source_prod_row['timestamp'],
  #     source_prod_row['filename'])
  #   class_ = self._get_class_instance(source)
  #   class_.get_product_specs(get_prods_from=filepath,to_csv=to_csv)
