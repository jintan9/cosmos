from constants.cosmos_addresses import all_addresses
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', default=False)
args = parser.parse_args()

for ibc_obj in all_addresses:
    print('')
    print(f'==== {ibc_obj.token} ====')
    ibc_obj.get_percent_delegation(recalculate_ranks=True, verbose=args.verbose)