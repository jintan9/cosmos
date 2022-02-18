from constants.cosmos_addresses import all_addresses

for ibc_obj in all_addresses:
    print('')
    print(f'==== {ibc_obj.token} ====')
    ibc_obj.get_percent_delegation(recalculate_ranks=True)