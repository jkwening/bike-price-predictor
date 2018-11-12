from utils.utils import TIMESTAMP, DATA_PATH
from ingestion.collect import Collect
from ingestion.ingest import Ingest
from ingestion.manifest import Manifest


class IngestionMediator:
  """
  Coordinates behavior for data collection and ingestion workflow across
  multiple classes involved. This is to allow decoupling between the
  classes involved and help clearly outline dependencies in workflow.
  """
  def __init__(self, data_path=DATA_PATH, manifest_filename='manifest.csv'):
    self._ingest = Ingest(mediator=self)
    self._collect = Collect(mediator=self, save_data_path=data_path)
    self._manifest = Manifest(mediator=self, path=data_path,
      filename=manifest_filename)

  #TODO: remove since redundant with update method
  def complete_update(self, drop_tables=False):
    """Run data ingestion from collection to ingest into database for all tables.
    
    This involves:
      1. collect both products and specs for all sources -skipping failed
      2. loading updated flat files into database accordingly
    """
    # attempt to scrape all sources - skipping those that fail
    self._collect.collect_all_products(get_specs=True, skip_failed=True)

    # attempt to load into database
    self._load_to_database(drop_tables=drop_tables)

  def _load_manifest_row_to_db(self, row: dict) -> bool:
    """Attempt to load the given csv file into database."""
    filepath = self._manifest.get_filepath_for_row(row)
    print(f'[_load_manifest_row_to_db] - filepath: {filepath}')
    if self._ingest.process_file(tablename=row['tablename'],
            filepath=filepath):
          # update data load status fields
          row['loaded'] =  True
          row['date_loaded'] = TIMESTAMP
          return True
    return False

  def update_manifest(self, rows: list) -> bool:
    """Update manifest with new row data."""
    return self._manifest.update(from_list=rows)

  def get_filepath_for_manifest_row(self, row: dict) -> str:
    return self._manifest.get_filepath_for_row(row)

  def _recreate_database_tables(self):
    """Recreate all database tables."""
    tablenames = self._ingest.get_db_tables()
    self._ingest.drop_table(tablenames)
    self._ingest.create_table(tablenames)
  
  def _load_to_database(self, sources: list=[], drop_tables=False):
    """Load data for specified sources into database."""
    if self._ingest.connect():
      if drop_tables:
        self._recreate_database_tables()

      loaded_rows = list()
      manifest_rows = self._manifest.get_rows_matching(sources=sources)

      for row in manifest_rows:
        print(f'loading to database: {row["filename"]}')
        if self._load_manifest_row_to_db(row):
          loaded_rows.append(row)
      
      self._ingest.close()

      # update loaded manifest rows
      self._manifest.update(from_list=loaded_rows)
    else:
      print(f'Database not updated - failed to connect!')

  def update(self, sources: list=[], from_manifest=True, drop_tables=False):
    """Update only for the listed sources.
    
    Use downloaded data files currently in manifest.csv by default, else
    collect data first updating manifest.csv accordingly.
    """
    if not from_manifest:
      self._collect.collect_from_sources(sources, get_specs=True, skip_failed=True)
    self._load_to_database(sources=sources,drop_tables=drop_tables)   

  def close_conn(self):
    self._ingest.close()


if __name__ == '__main__':
  mediator = IngestionMediator()
  mediator.complete_update()
