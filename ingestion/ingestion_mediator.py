import os
import pandas as pd

# Import package modules
from ingestion.collect import Collect
from ingestion.ingest import Ingest
from ingestion.cleaner import Cleaner
from ingestion.manifest import Manifest, MungedManifest
from utils.utils import TIMESTAMP, RAW_DATA_PATH, MUNGED_DATA_PATH
from utils.utils import COMBINED_MUNGED_PATH


class IngestionMediator:
    """
  Coordinates behavior for data collection and ingestion workflow across
  multiple classes involved. This is to allow decoupling between the
  classes involved and help clearly outline dependencies in workflow.
  """

    def __init__(self, data_path=RAW_DATA_PATH, manifest_filename='manifest.csv',
                 munged_data_path=MUNGED_DATA_PATH,
                 combined_munged_path=COMBINED_MUNGED_PATH,
                 munged_manifest_filename='munged_manifest.csv'):
        self._munged_data_path = munged_data_path
        self._combined_munged_path = combined_munged_path
        self._ingest = Ingest(mediator=self)
        self._collect = Collect(mediator=self, save_data_path=data_path)
        self._cleaner = Cleaner(mediator=self, save_data_path=munged_data_path)
        self._manifest = Manifest(mediator=self, path=data_path,
                                  filename=manifest_filename)
        self._munged_manifest = MungedManifest(mediator=self, path=munged_data_path,
                                               filename=munged_manifest_filename)

    def collect_sources(self, sources: list, get_specs=False, skip_failed=True):
        """Collect products from sources."""
        self._collect.collect_from_sources(sources=sources, get_specs=get_specs,
                                           skip_failed=skip_failed)

    def collect_all(self, get_specs=False, skip_failed=True):
        """Collect products from all sources."""
        self._collect.collect_all_products(get_specs, skip_failed)

    # TODO: error handling if product file doesn't exist?!?!
    def extract_specs(self, source: str, bike_type: str = 'all'):
        """Collect specs for sources."""
        self._collect.collect_specs_matching(source=source, bike_type=bike_type)

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

    # TODO: refactor to load process, excluding collect steps
    def update(self, sources: list, from_manifest=True,
               collect_only=False, drop_tables=True,
               get_specs=True):
        """Update only for the listed sources.
    
    Use downloaded data files currently in manifest.csv by default, else
    collect data first updating manifest.csv accordingly.
    """
        if not from_manifest or collect_only:
            print('collecting...')
            self._collect.collect_from_sources(sources, get_specs=get_specs,
                                               skip_failed=True)

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
        """Get spec fieldnames from all spec data files in manifest.csv."""
        return self._manifest.get_unique_spec_fieldnames()

    def aggregate_data(self, from_raw=False, to_csv=True):
        """Aggregate transformed data into single dataframe.

        Args:
            from_raw(bool): If True, clean each raw data file and then
                aggregate; else, aggregate using munged manifest.
            to_csv(bool): If True, save combined transformed data to csv.
        """
        # Initialize empty df for combining purpose
        agg_df = pd.DataFrame(columns=self._cleaner.get_field_names())

        # Utilize transform_from_manifest() when from_raw=True
        if from_raw:
            self.transform_from_manifest(update_munged_manifest=False,
                                         save_cleaned_data=False,
                                         combine=True, save_combined=to_csv)
        # Combine latest munged data using munged manifest as source
        else:
            for row in self._munged_manifest.get_all_rows():
                munged_df = pd.read_csv(self._munged_manifest.get_filepath_for_row(row))
                agg_df = agg_df.append(munged_df, ignore_index=True, sort=False)

        if to_csv:
            fname = f'combined_munged_{TIMESTAMP}.csv'
            path = os.path.join(self._combined_munged_path, fname)
            agg_df.to_csv(path, index=False, encoding='utf-8')

    def transform_raw_data(self, source, bike_type='all'):
        """Clean and merge raw data files for given source."""
        munged_df = self._cleaner.clean_source(source, bike_type)
        row_data = self._cleaner.save_munged_df(df=munged_df, source=source)
        self.update_munged_manifest(rows=[row_data])
        return row_data

    def transform_from_manifest(self, update_munged_manifest=True,
                                save_cleaned_data=True,
                                combine=False, save_combined=False):
        """Using manifest as source, process all available data.

        Args:
            update_munged_manifest(bool): If True, update munged manifest.
            save_cleaned_data(bool): If True, save each transformed source.
            combine(bool): If True, aggregate munged data into single dataframe.
            save_combined(bool): If True, save the combined dataframe to csv.
        """
        # Initialize empty df for combining purpose
        agg_df = pd.DataFrame(columns=self._cleaner.get_field_names())

        # Get all unique source, bike_type pairings in manifest
        source_pairs = self._manifest.get_table_pairs()
        for source, label_dict in source_pairs.items():
            # Iterate through each pairing and clean raw data
            for bike_type in label_dict:
                try:
                    munged_df = self._cleaner.clean_source(source, bike_type)
                except ValueError:
                    continue
                # If combine, append to aggregate dataframe
                if combine or save_combined:
                    agg_df = agg_df.append(munged_df, ignore_index=True,
                                           sort=False)
                # Save transformed data if requested
                if save_cleaned_data or update_munged_manifest:
                    row = self._cleaner.save_munged_df(df=munged_df, source=source)
                    # Update munged manifest if requested
                    if update_munged_manifest:
                        self._munged_manifest.update(from_list=[row])

        # Save combined if requested
        if save_combined:
            fname = f'combined_munged_{TIMESTAMP}.csv'
            path = os.path.join(self._munged_data_path, fname)
            agg_df.to_csv(path, index=False, encoding='utf-8')

    def update_munged_manifest(self, rows: list) -> bool:
        """Update munged manifest with new row data."""
        return self._munged_manifest.update(from_list=rows)
