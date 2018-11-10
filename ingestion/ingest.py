"""Modules for loading raw data files into appropriate tables in the database"""

import psycopg2


class Ingest:
  """Handles loading data csv files into the database tables."""
  def __init__(self, mediator):
    self._mediator = mediator
    self._conn = None
    self._SPEC_FIELDNAMES = {
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
    self._COPY_FROM_STATEMENT = """
      COPY %s FROM STDIN WITH CSV HEADER DELIMITER AS ','
      """
    self._tables = set()

  def connect(self):
    """Connect to PostgreSQL database server. """
    try:
      self._conn = psycopg2.connect('host=localhost dbname=bike_pricer user=postgres')
      return True
    except (Exception, psycopg2.DatabaseError) as e:
      print(e)
      return False

  #TODO: seems unnecesary - remove once confirmed
  def close(self):
    """Close database server connection."""
    if self._conn is not None:
      self._conn.close()
      print('Database connection is closed.')
    else:
      print('Not connected to database.')

  def _generate_specs_create_table_sql_statement(self, fieldnames):
    """Generate the appropriate SQL statement for product_specs table."""
    statement = """CREATE TABLE product_specs (
      site VARCHAR(100) NOT NULL,
      product_id VARCHAR(100) NOT NULL,
      PRIMARY KEY (site, product_id),"""

    for fieldname in fieldnames:
      statement = (statement + '\n{} VARCHAR(500),').format(fieldname)
    
    return statement[:-1] + ')'
    
  def get_db_tables(self):
    """Return tablenames in database."""
    cur = self._conn.cursor()
    cur.execute("""SELECT table_name FROM information_schema.tables
       WHERE table_schema = 'public'""")
    for table in cur.fetchall():
        self._tables.add(table[0])
    return self._tables

  def create_table(self, tablenames):
    """Create tables in database."""
    commands = list()  # list of create table commands to execute

    if 'products' in tablenames:
      commands.append(
        """
        CREATE TABLE products (
          bike_type VARCHAR(50),
          site VARCHAR(100) NOT NULL,
          product_id VARCHAR(100) NOT NULL,
          PRIMARY KEY (site, product_id),
          href VARCHAR(1000),
          brand VARCHAR(50),
          description VARCHAR(100),
          price FLOAT,
          msrp FLOAT
        )
        """
      )

    if 'product_specs' in tablenames:
      commands.append(self._generate_specs_create_table_sql_statement(
        self._SPEC_FIELDNAMES))
    
    success = False
    try:
      cur = self._conn.cursor()
      for command in commands:
        cur.execute(command)
      self._conn.commit()
      success = True
    except (Exception, psycopg2.DatabaseError) as e:
      print(e)
    finally:
      cur.close()
      return success

  def drop_table(self, tablenames: list) -> bool:
    """Drop tables from database."""
    success = False
    try:
      cur = self._conn.cursor()
      for table in tablenames:
        statement = """DROP TABLE %s""" % table
        cur.execute(statement)
      self._conn.commit()
      success = True
    except (Exception, psycopg2.DatabaseError) as e:
      print(e)
    finally:
      cur.close()
      return success

  def process_file(self, tablename, filepath):
    """Load file into database."""
    # create table if it doesn't exist already
    if tablename not in self.get_db_tables():
      if not self.create_table(tablenames=[tablename]):
        raise psycopg2.DatabaseError

    success = False
    with open(filepath, encoding='utf-8') as f:
      try:
        cur = self._conn.cursor()
        cur.copy_expert(sql=self._COPY_FROM_STATEMENT % tablename, file=f)
        self._conn.commit()
        success = True
      except (Exception, psycopg2.DatabaseError) as e:
        print(e)
      finally:
        cur.close()
        return success
