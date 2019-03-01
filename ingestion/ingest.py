"""Module for loading raw data files into appropriate tables in the database"""

import psycopg2
from csv import DictReader

from utils.utils import config


class Ingest:
    """Handles loading data csv files into the database tables."""

    def __init__(self, mediator):
        self._mediator = mediator
        self._conn = None
        self._SPEC_FIELDNAMES = set()
        self._SPEC_FIELDNAMES_DEFAULT = {
            'levers', 'frame_seatpost', 'rotors', 'derailleur_pull', 'frame_material',
            'weight', 'wheel_size', 'front_axle', 'frame_fork', 'wheelset',
            'v_brake_studs', 'suspension', 'front_derailleur_mount', 'material',
            'display', 'seatpost_size', 'bottom_bracket_type', 'brake_type',
            'iscg_tabs', 'grips_bar_tape', 'cassette_range', 'compatibility',
            'rack_mounts', 'headlight', 'saddle', 'grips', 'bar_tape', 'tire_size',
            'cable_routing', 'frame_replaceable_dropout', 'fenders', 'seatpost_clamp',
            'pedals', 'crankset', 'sun_rain_cover', 'accessories', 'fork',
            'frame_bottom_bracket', 'frame_weight', 'frame_fork_travel', 'bars',
            'bottle_mount_sets', 'recommended_use', 'rear_carrier', 'extras',
            'steer_diameter', 'handlebar_width', 'hubs', 'rear_derailleur', 'stem',
            'chain', 'handlebar_rise', 'chainring_sizes', 'rear_travel', 'frame',
            'replaceable_hanger', 'body_material', 'recommended_fork_travel',
            'rear_shock', 'battery', 'rear_axle', 'manufacturer_warranty', 'fork_material',
            'front_travel', 'frame_type', 'rear_wheel_spacing', 'crank_arm_length',
            'taillight', 'rack_mount', 'head_tube_diameter', 'brake_levers',
            'handlebar_sweep', 'weight_capacity', 'dropouts', 'tape_grips', 'drive_unit',
            'handlebar', 'front_derailleur', 'cassette', 'shifters', 'headset',
            'compatible_components', 'headset_included', 'fork_travel',
            'cog_freewheel', 'standover_height', 'grips_tape', 'skewers', 'bottom_bracket',
            'brakes', 'stem_length', 'offset_rake', 'headset_size',
            'dimensions', 'brakeset', 'seat_collar', 'handlebar_drop', 'tires',
            'seatpost_diameter', 'seatpost', 'frame_headset_size',
            'frame_front_derailleur', 'disc_mount'
        }
        self._PRODUCTS_TABLENAMES = ['products', 'imported_products']
        self._SPECS_TABLENAMES = ['product_specs', 'imported_specs']
        self._databases = {
          'local': 'db_local',
          'staging': 'db_staging',
          'prod': 'db_prod'
        }

    def connect(self, database='local'):
        """Connect to PostgreSQL database server. """

        try:
            section = self._databases.get(database, 'db_local')
            params = config(section=section)
            print('Connecting to the PostgreSQL database...')
            self._conn = psycopg2.connect(**params)
            return True
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            self._conn.rollback()
            return False

    def close(self):
        """Close database server connection."""
        if self._conn is not None:
            self._conn.close()
            print('Database connection is closed.')
        else:
            print('Not connected to database.')

    def get_required_tablenames(self) -> list:
        """Return default tablenames needed for data pipeline ingestion."""
        return self._PRODUCTS_TABLENAMES + self._SPECS_TABLENAMES

    def _generate_specs_create_table_sql_statement(self, tablename, fieldnames):
        """Generate the appropriate SQL statement for product_specs table."""
        statement = """CREATE TABLE IF NOT EXISTS %s (
      site VARCHAR(100) NOT NULL,
      product_id VARCHAR(100) NOT NULL,
      PRIMARY KEY (site, product_id),""" % tablename

        for fieldname in fieldnames:
            statement = (statement + '\n{} VARCHAR(500),').format(fieldname)

        return statement[:-1] + ')'

    def get_db_tables(self) -> set:
        """Return tablenames in database."""
        result = set()
        cur = self._conn.cursor()
        cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
        self._conn.commit()
        for table in cur.fetchall():
            result.add(table[0])
        cur.close()
        return result

    def create_table(self, tablename: str) -> bool:
        """Create tables in database."""
        if tablename in self._PRODUCTS_TABLENAMES:
            command = """CREATE TABLE IF NOT EXISTS %s (
        bike_type VARCHAR(50),
        site VARCHAR(100) NOT NULL,
        product_id VARCHAR(100) NOT NULL,
        PRIMARY KEY (site, product_id),
        href VARCHAR(1000),
        brand VARCHAR(50),
        description VARCHAR(100),
        price FLOAT,
        msrp FLOAT)""" % tablename

        if tablename in self._SPECS_TABLENAMES:
            if self._SPEC_FIELDNAMES is None:
                self._SPEC_FIELDNAMES = self._mediator.get_spec_fieldnames()

            command = self._generate_specs_create_table_sql_statement(tablename,
                                                                      self._SPEC_FIELDNAMES)

        success = False
        try:
            cur = self._conn.cursor()
            cur.execute(command)
            self._conn.commit()
            success = True
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            self._conn.rollback()
        finally:
            cur.close()
            return success

    def drop_table(self, tablenames: list) -> bool:
        """Drop tables from database."""
        success = False
        try:
            cur = self._conn.cursor()
            for table in tablenames:
                statement = """DROP TABLE IF EXISTS %s""" % table
                cur.execute(statement)
            self._conn.commit()
            success = True
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            self._conn.rollback()
        finally:
            cur.close()
            return success

    def _generate_copy_expert_statement(self, tablename, fieldnames):
        """Generate the appropriate SQL statement for product_specs table."""
        statement = """COPY %s (""" % tablename

        for fieldname in fieldnames:
            statement = (statement + """\n{},""").format(fieldname)

        return statement[:-1] + """) FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"""

    def process_file(self, tablename: str, filepath: str):
        """Load file into database."""
        success = False
        try:
            # load csv into temp table - create if doesn't exist
            with open(filepath, encoding='utf-8') as f:
                cur = self._conn.cursor()
                fieldnames = DictReader(f).fieldnames
                if tablename in self._PRODUCTS_TABLENAMES:
                    tmp_tablename = 'imported_products'
                else:
                    tmp_tablename = 'imported_specs'
                    self._check_for_new_specs_columns(fieldnames)

                self.create_table(tmp_tablename)
                cur.copy_expert(sql=self._generate_copy_expert_statement(tmp_tablename,
                                                                         fieldnames), file=f)
                self._conn.commit()

            # upsert into real table - create if doesn't exist
            self.create_table(tablename)
            statement = """INSERT INTO %s
        SELECT * FROM %s
        ON CONFLICT DO NOTHING""" % (tablename, tmp_tablename)
            cur.execute(statement)
            self._conn.commit()

            # don't keep temp table
            self.drop_table([tmp_tablename])

            success = True
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            self._conn.rollback()
        finally:
            cur.close()
            return success

    def _check_for_new_specs_columns(self, fieldnames: list):
        """Add new fieldname to master specs list and update real table columns."""
        exclude_fieldnames = ['site', 'product_id']  # exclude primary key fieldnames
        if self._SPEC_FIELDNAMES is None:
            self._SPEC_FIELDNAMES = self._mediator.get_spec_fieldnames()

        new_columns = set()
        for fieldname in fieldnames:
            if fieldname not in self._SPEC_FIELDNAMES and fieldname not in exclude_fieldnames:
                self._SPEC_FIELDNAMES.add(fieldname)
                new_columns.add(fieldname)

        # add new columns to table iff it already exists
        if new_columns and 'product_specs' in self.get_db_tables():
            with self._conn as conn:
                with conn.cursor() as cur:
                    for fieldname in new_columns:
                        cur.execute(
                            """ALTER TABLE IF EXISTS product_specs
                ADD COLUMN IF NOT EXISTS %s VARCHAR(500)
              """ % fieldname)

        return new_columns

    def set_spec_fieldnames(self, fieldnames):
        """Update product specs fieldnames."""
        self._SPEC_FIELDNAMES = fieldnames

    def get_column_names(self, tablename: str) -> list:
        """Return column names for specified table."""
        try:
            result = list()
            cur = self._conn.cursor()
            cur.execute("""SELECT * FROM %s WHERE FALSE""" % tablename)
            self._conn.commit()

            for column in cur.fetchall():
                result.append(column[0])
            return result
        except (Exception, psycopg2.DatabaseError) as e:
            print(e)
            self._conn.rollback()
        finally:
            cur.close()
            return result
