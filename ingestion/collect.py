"""Module for scraping websites to collect raw data."""

import os

from utils.utils import DATA_PATH
from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.nashbar import NashBar
from scrapers.performance_bike import PerformanceBikes
from ingestion.manifest import Manifest

SOURCES = ['competitive', 'nashbar', 'performance']

def _get_class_instance(source):
  """Get appropriate scraper class instance for given source."""
  if source == 'competitive':
    return CompetitiveCyclist()
  elif source == 'nashbar':
    return NashBar()
  elif source == 'performance':
    return PerformanceBikes()
  else:
    raise ValueError(f'Invalid source: {source} value.')

def collect_all(get_specs=True):
  """Collect raw data file from all sources."""
  for source in SOURCES:
    collect_from_source(source, get_specs=get_specs)

def collect_from_source(source, get_specs=True):
  """Collect raw data file for specified source."""
  class_ = _get_class_instance(source)
  class_.get_all_available_prods(get_specs=get_specs)

#FIXME: think through how to handle multiple competitive sources
def get_all_specs(to_csv=True):
  manifest = Manifest()
  for source in SOURCES:
    get_specs_for_source(source, manifest=manifest, to_csv=to_csv)

#FIXME: think through how to handle multiple competitive sources
def get_specs_for_source(source, manifest=None, to_csv=True):
  """Get specs for ..."""
  if manifest is None:
    manifest = Manifest()
  
  source_prod_row = None
  for row in manifest.get_product_rows():
    if row['source'] == source:
      source_prod_row = row
      break

  if source_prod_row is None:
    raise ValueError(f'{source} does not have products row in manifest!')
  
  filepath = os.path.join(DATA_PATH, source_prod_row['timestamp'],
    source_prod_row['filename'])
  class_ = _get_class_instance(source)
  class_.get_product_specs(get_prods_from=filepath,to_csv=to_csv)
