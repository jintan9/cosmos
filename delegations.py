import argparse

from constants.cosmos_addresses import list_address

ONE_MILLION = 1000 * 1000

parser = argparse.ArgumentParser()
parser.add_argument('--name', choices=[x for x in list_address])
args = parser.parse_args()

precise = True
show_votes = False

addresses = list_address[args.name]
big_total = 0
for ibc_obj in addresses:
    print('')
    print(ibc_obj.address, ibc_obj.token)

    ibc_obj.get_percent_delegation()
    ibc_obj.get_unbounding_info()
    ibc_obj.get_redelegation_info()

    if precise:
        ibc_obj.get_precise_infos()

    big_total += ibc_obj.get_total_value(verbose=True)

    if show_votes:
        ibc_obj.show_ongoing_proposals()

print(f'BIG TOTAL : {big_total} USDC')