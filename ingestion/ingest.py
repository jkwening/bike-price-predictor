"""Modules for loading raw data files into appropriate tables in the database"""

import psycopg2


_CONN = None
SPEC_FIELDNAMES = {
  'levers', 'frame_seatpost', 'rotors', 'derailleur_pull', 'frame_material',
  'weight', 'wheel_size', 'front_axle', 'frame_fork', 'wheelset',
  'v-brake_studs', 'suspension', 'front_derailleur_mount', 'material',
  'display', 'seatpost_size', 'bottom_bracket_type', 'brake_type',
  'iscg_tabs', 'grips/bar_tape', 'cassette_range', 'compatibility',
  'rack_mounts', 'headlight', 'saddle', 'grips', 'bar_tape', 'tire_size',
  'cable_routing', 'frame_replaceable_dropout', 'fenders', 'seatpost_clamp',
  'pedals', 'crankset', 'sun_/_rain_cover', 'accessories', 'fork',
  'frame_bottom_bracket', 'frame_weight', 'frame_fork_travel', 'bars',
  'bottle_mount_sets', 'recommended_use', 'rear_carrier', 'extras',
  'steer_diameter', 'handlebar_width', 'hubs', 'rear_derailleur', 'stem',
  'chain', 'handlebar_rise', 'chainring_sizes', 'rear_travel', 'frame',
  'replaceable_hanger', 'source', 'body_material', 'recommended_fork_travel',
  'rear_shock', 'battery', 'rear_axle', 'manufacturer_warranty', 'fork_material',
  'front_travel', 'frame_type', 'rear_wheel_spacing', 'crank_arm_length',
  'taillight', 'rack_mount', 'head_tube_diameter', 'brake_levers',
  'handlebar_sweep', 'weight_capacity', 'dropouts', 'tape/grips', 'drive_unit',
  'handlebar', 'front_derailleur', 'cassette', 'shifters', 'headset',
  'compatible_components', 'headset_included', 'fork_travel',
  'cog/freewheel', 'standover_height', 'grips/tape', 'skewers', 'bottom_bracket',
  'product_id', 'brakes', 'stem_length', 'offset_(rake)', 'headset_size',
  'dimensions', 'brakeset', 'seat_collar', 'handlebar_drop', 'tires',
  'seatpost_diameter', 'seatpost', 'frame_headset_size',
  'frame_front_derailleur', 'disc_mount'
  }

def connect():
  """Connect to PostgreSQL database server. """
  try:
    _CONN = psycopg2.connect('host=localhost dbname=bike_pricer user=postgres')
    return _CONN
  except (Exception, psycopg2.DatabaseError) as e:
    print(e)
    return None

def close():
  """Close database server connection."""
  if _CONN is not None:
    _CONN.cose()
    print('Database connection is closed.')
  else:
    print('Not connected to database.')

def create_table(db_conn=None, tablenames=['products']):
  """Create tables in database."""
  if db_conn is None:
    db_conn = connect()
  
  commands = list()  # list of create table commands to execute

  if 'products' in tablenames:
    commands.append(
      """
      CREATE TABLE products (
        source VARCHAR(100) NOT NULL,
        product_id VARCHAR(100) NOT NULL,
        PRIMARY KEY (source, product_id),
        href VARCHAR(1000),
        brand VARCHAR(50),
        description VARCHAR(100),
        price FLOAT,
        msrp FLOAT
      )
      """
    )

  if 'products_specs' in tablenames:
    #TODO: figure out unique headers and populate table
    pass
  
  try:
    cur = db_conn.cursor()
    for command in commands:
      cur.execute(command)
    cur.close()
    db_conn.commit()
  except (Exception, psycopg2.DatabaseError) as e:
    print(e)
  finally:
    db_conn.close()
