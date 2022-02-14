import requests
from cosmos_addresses import list_tokens


def show_validators(ibc_obj):
    print('')
    print(f'==== {ibc_obj.token} ====')
    list_validators = requests.get(ibc_obj.url_validators).json()
    ranks_validators = dict()
    for val in list_validators:
        ranks_validators[val['operator_address']] = dict(rank=val['rank'], moniker=val['moniker'])

    print(ibc_obj.api + 'staking/delegators/' + ibc_obj.address + '/delegations')
    validators = requests.get(ibc_obj.api + 'staking/delegators/' + ibc_obj.address + '/delegations').json()
    my_delegation = validators['result']
    total = sum([int(x['balance']['amount']) for x in my_delegation])
    print('TOTAL', total)
    for delegation in my_delegation:
        print(ranks_validators[delegation['delegation']['validator_address']])
        print('%s %%' % round(float(delegation['balance']['amount']) * 100 / total, 2))


for token_infos in list_tokens:
    show_validators(token_infos)