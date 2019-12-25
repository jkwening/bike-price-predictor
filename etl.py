"""
ETL module manages the data ingestion workflow.
"""
import argparse

from ingestion.ingestion_mediator import IngestionMediator
from utils.utils import SOURCES

MEDIATOR = IngestionMediator()


def main(args):
    # Handle collect workflow request
    if args.ETL == 'collect':
        MEDIATOR.collect_sources(sources=args.sources,
                                 get_specs=args.get_specs,
                                 skip_failed=args.skip_failed)

    # Collect specs for given source products.
    if args.ETL == 'extract':
        for source in args.sources:
            MEDIATOR.extract_specs(source=source)

    # Transform raw data files
    if args.ETL == 'clean':
        for source in args.sources:
            MEDIATOR.transform_raw_data(source=source, bike_type='all')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ETL workflow module.')
    parser.add_argument('ETL', choices=['collect', 'clean', 'extract'],
                        help='ETL workflow step to complete.')
    parser.add_argument('-s', dest='sources', nargs='+', default=SOURCES,
                        help='Site sources to process. Defaults to all sources if none provided.')
    parser.add_argument('-specs', action='store_true', dest='get_specs',
                        default=False,
                        help='Collect product specs after collecting products. ')
    parser.add_argument('-e', action='store_false', dest='skip_failed',
                        default=True,
                        help='Raise errors and don\'t skip failed processes.')
    main(args=parser.parse_args())
