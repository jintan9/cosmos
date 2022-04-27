from constants.cosmos_addresses import all_addresses, test_addresses
import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--verbose', default=False)
args = parser.parse_args()

if args.verbose == 'true':
    addresses = test_addresses
else:
    addresses = all_addresses

for ibc_obj in addresses:
    print('')
    print(f'==== {ibc_obj.token} ====')
    try:
        ibc_obj.get_percent_delegation(recalculate_ranks=True, verbose=args.verbose)
    except AssertionError as e:
        print('ERROR', e)
        print(ibc_obj.get_delegation_url())
        print(requests.get(ibc_obj.get_delegation_url()).__dict__)