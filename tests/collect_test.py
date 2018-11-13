import unittest

from ingestion.collect import Collect
from ingestion.ingestion_mediator import IngestionMediator
from scrapers.competitive_cyclist import CompetitiveCyclist
from scrapers.nashbar import NashBar
from scrapers.performance_bike import PerformanceBikes
from tests.unit_test_utils import DATA_PATH, TEST_DATA_PATH


class ManifestTestCase(unittest.TestCase):
  def setUp(self):
    self._mediator = IngestionMediator(data_path=DATA_PATH)
    self._collect = Collect(mediator=self._mediator, save_data_path=DATA_PATH)

  def test_get_class_instance(self):
    """Unit test for Collect._get_class_instance()"""
    # case 'performance'
    result = self._collect._get_class_instance(source='performance')
    self.assertTrue(isinstance(result, PerformanceBikes),
      msg=f'{result} should be an instance of PerformanceBike class.')

    # case 'competitive'
    result = self._collect._get_class_instance(source='competitive')
    self.assertTrue(isinstance(result, CompetitiveCyclist),
      msg=f'{result} should be an instance of Competitive class.')
      
    # case 'nashbar'
    result = self._collect._get_class_instance(source='nashbar')
    self.assertTrue(isinstance(result, NashBar),
      msg=f'{result} should be an instance of Nashbar class.')
      
    # case invalid
    self.assertRaises(ValueError, self._collect._get_class_instance, 'hello world')

  def test_collect_products_from_source(self):
    """Test Collect.collect_products_from_source(source='competitive', get_specs=True)."""
    self._mediator = IngestionMediator(data_path=DATA_PATH,
      manifest_filename='collect_manifest.csv')
    self._collect = Collect(mediator=self._mediator, save_data_path=DATA_PATH)
    self._collect.collect_products_from_source(source='competitive', get_specs=True)

  def test_collect_specs_matching(self):
    """Test for Collect.collect_specs_matching()."""
    self._collect.collect_specs_matching(source='competitive', bike_type='kid')


if __name__ == '__main__':
    unittest.main()
