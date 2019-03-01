from ingestion.collect import Collect
from ingestion.ingest import Ingest
from ingestion.manifest import Manifest
from utils.utils import TIMESTAMP, DATA_PATH

# Module constants
SITES = ['competitive', 'nashbar', 'performance', 'rei', 'wiggle',
         'citybikes']


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

    # TODO: remove since redundant with update method
    def complete_update(self, collect_only=False, drop_tables=False):
        """Run data ingestion from collection to ingest into database for all tables.
    
    This involves:
      1. collect both products and specs for all sources -skipping failed
      2. loading updated flat files into database accordingly
    """
        # attempt to scrape all sources - skipping those that fail
        self._collect.collect_all_products(get_specs=True, skip_failed=True)

        # attempt to load into database
        if not collect_only:
            self._load_to_database(drop_tables=drop_tables)

    def _load_manifest_row_to_db(self, row: dict) -> bool:
        """Attempt to load the given csv file into database."""
        filepath = self._manifest.get_filepath_for_row(row)
        print(f'[_load_manifest_row_to_db] - filepath: {filepath}')
        if self._ingest.process_file(tablename=row['tablename'],
                                     filepath=filepath):
            # update data load status fields
            row['loaded'] = True
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
        if not tablenames:  # get default tablenames if non currently active
            tablenames = self._ingest.get_required_tablenames()

        # get appropriate fieldnames for product_specs table
        fieldnames = self.get_spec_fieldnames()
        self._ingest.set_spec_fieldnames(fieldnames)

        self._ingest.drop_table(tablenames)
        for tablename in tablenames:
            self._ingest.create_table(tablename)

    def _load_to_database(self, sources: list = [], drop_tables=False):
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

    def update(self, sources: list = [], from_manifest=True,
               collect_only=False, drop_tables=True):
        """Update only for the listed sources.
    
    Use downloaded data files currently in manifest.csv by default, else
    collect data first updating manifest.csv accordingly.
    """
        if not from_manifest or collect_only:
            print('collecting...')
            self._collect.collect_from_sources(sources, get_specs=True, skip_failed=True)

        if not collect_only:
            print('loading to db...')
            self._load_to_database(sources=sources, drop_tables=drop_tables)

    def update_specs_matching(self, source: str, bike_type: str) -> bool:
        if self._ingest.connect():
            spec_row_data = self._collect.collect_specs_matching(source, bike_type)
            return self._load_manifest_row_to_db(row=spec_row_data)
        return False

    def get_rows_matching(self, sources: list = [], tablenames: list = [],
                          bike_types: list = [], loaded: list = []) -> list:
        """Return the manifest row matching request criteria."""
        return self._manifest.get_rows_matching(sources=sources,
                                                tablenames=tablenames, bike_types=bike_types, loaded=loaded)

    def close_conn(self):
        self._ingest.close()

    def get_spec_fieldnames(self):
        """Get spec fieldnames from data all spec files in manifest.csv."""
        return self._manifest.get_unique_spec_fieldnames()


if __name__ == '__main__':
    # # Configure command line parsing
    # parser = argparse.ArgumentParser(description='Update data for listed sources, all sources if none listed.')
    # parser.add_argument('sources', metavar='S', type='string', nargs='?',
    #   choices=SITES, default=[],
    #   help='Data source options: "competitive", "nashbar", "performance", "rei", "wiggle"')
    # mode = parser.add_mutually_exclusive_group(required=True)
    # mode.add_argument('-m', '--from-manifest', dest='from_manifest', action='store_true',
    #   help='Use downloaded data files currently in manifest.csv', default=False)
    # mode.add_argument('-c', '--collect-only', dest='collect_only', action='store_true',
    #   help='Collect data first updating manifest.csv accordingly', default=False)
    #
    # # Process args
    # args = parser.parse_args()
    mediator = IngestionMediator()
    # mediator.update(sources=args.sources, from_manifest=args.from_manifest,
    #   collect_only=args.collect_only, drop_tables=False)
    mediator.update(sources=[], from_manifest=True, collect_only=False)
