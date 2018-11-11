import unittest

from ingestion.ingest import Ingest, psycopg2
from ingestion.ingestion_mediator import IngestionMediator
from tests.unit_test_utils import DATA_PATH, TEST_DATA_PATH, os


class ManifestTestCase(unittest.TestCase):
  def setUp(self):
    self._mediator = IngestionMediator(data_path=DATA_PATH)
    self._ingest = Ingest(mediator=self._mediator)

  def test_connect_close(self):
    """Test Ingest.connect() and Ingest.close()."""
    # case 1: init with self._conn = None
    self.assertIsNone(self._ingest._conn,
      msg='class should initialize with self._conn = None')

    # case 2: connect successfully
    self.assertTrue(self._ingest.connect(),
      msg='Check if database server is running!')
    self.assertTrue(isinstance(self._ingest._conn,
      psycopg2.extensions.connection),
      msg=f'Incorrect conn type: {self._ingest._conn}')
    self.assertEqual(0, self._ingest._conn.closed,
      msg=f'Incorrect closed value: {self._ingest._conn.closed}')

    # case 3: closed successfully
    self._ingest.close()
    self.assertEqual(1, self._ingest._conn.closed,
      msg=f'Incorrect closed value: {self._ingest._conn.closed}')

  def test_table_management_methods(self):
    """Test create_table, drop_table, and get_db_tables methods."""
    prods_tablename = 'products'
    specs_tablename = 'product_specs'

    self._ingest.connect()
    
    # ensure test tables don't exist in db
    current_db_tables = self._ingest.get_db_tables()
    print(f'[Ensure 1] - current tables: {current_db_tables}')
    for table in [prods_tablename, specs_tablename]:
      if table in current_db_tables:
        self.assertTrue(self._ingest.drop_table(tablenames=[table]),
          msg=f'Failed to drop {table} table')
    current_db_tables = self._ingest.get_db_tables()
    print(f'[Ensure 2] - current tables: {current_db_tables}')
    self.assertTrue(prods_tablename not in current_db_tables,
      msg=f'{prods_tablename} should not still be in database.')
    self.assertTrue(specs_tablename not in current_db_tables,
      msg=f'{specs_tablename} should not still be in database.')

    # add test tables into database
    self.assertTrue(self._ingest.create_table(
      tablenames=[specs_tablename, prods_tablename]),
      msg='Failed to create test tables.')
    current_db_tables = self._ingest.get_db_tables()
    print(f'[Add] - current tables: {current_db_tables}')
    self.assertTrue(prods_tablename in current_db_tables,
      msg=f'{prods_tablename} should now be in database.')
    self.assertTrue(specs_tablename in current_db_tables,
      msg=f'{specs_tablename} should now be in database.')
    
    # close connection
    self._ingest.close()

  def test_process_file(self):
    """Test Ingest.process_file()."""
    self._ingest.connect()
    self._ingest.drop_table(tablenames=['product_specs'])
    comp_road_spec_filepath = os.path.join(TEST_DATA_PATH, '11102018',
      'competitive_specs_road.csv')
    result = self._ingest.process_file(tablename='product_specs',
      filepath=comp_road_spec_filepath)
    self.assertTrue(result, msg='Should load file into database.')


if __name__ == '__main__':
    unittest.main()
