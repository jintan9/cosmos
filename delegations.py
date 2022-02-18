import argparse

from constants.cosmos_addresses import list_address

ONE_MILLION = 1000 * 1000

parser = argparse.ArgumentParser()
parser.add_argument('--name', choices=[x for x in list_address])
args = parser.parse_args()

precise = True
show_votes = False

addresses = list_address[args.name]['all']
for ibc_obj in addresses:
    print('')
    print(ibc_obj.address, ibc_obj.token)

    ibc_obj.get_percent_delegation()
    ibc_obj.get_unbounding_info()
    ibc_obj.get_redelegation_info()

    if precise:
        if ibc_obj.token == 'OSMO':
            print('OSMO MORE PRECISE INFO')
            ibc_obj.set_price_by_token()
            ibc_obj.get_balance()
            ibc_obj.get_pools()
            ibc_obj.get_precise_pools()
        elif ibc_obj.token in ['ATOM', 'JUNO']:
            print(f'{ibc_obj.token} MORE PRECISE INFO')
            ibc_obj.get_price_by_token_custom()
            ibc_obj.get_balance()

    if show_votes:
        ibc_obj.show_ongoing_proposals()
