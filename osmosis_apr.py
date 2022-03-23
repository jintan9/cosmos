import requests
import datetime

from ibc_model import IBCToken

start_time = datetime.datetime.now()
my_pools = ['1', '560', '578', '601', '604', '606', '611']

def get_pool_apr(id_pool):
    infos = requests.get(f'https://api-osmosis.imperator.co/apr/v1/{id_pool}').json()

    first_apr = round(infos[0]['apr_list'][0]['apr_14d'], 2)
    if len(infos[0]['apr_list']) == 1:
        # No external incentive
        return round(first_apr, 2)

    total_apr = first_apr + round(infos[0]['apr_list'][1]['apr_14d'], 2)
    print(f'POOL {id_pool} {pool_tokens} : {total_apr} %')
    return round(total_apr, 2)


prices_by_token = IBCToken.get_price_by_token()
infos_pool = requests.get('https://lcd-osmosis.keplr.app/osmosis/gamm/v1beta1/pools?pagination.limit=750').json()['pools']
all_pools = dict()

print('GETTING ALL POOLS')
for pool in infos_pool:
    try:
        first_token = prices_by_token[pool['poolAssets'][0]['token']['denom']]['name']
        sec_token = prices_by_token[pool['poolAssets'][1]['token']['denom']]['name']
        all_pools[pool["id"]] = f'{first_token}/{sec_token}'
    except KeyError:
        all_pools[pool['id']] = f'error for {pool["id"]}'

incentive_pool = requests.get('https://lcd-osmosis.keplr.app/osmosis/pool-incentives/v1beta1/incentivized_pools').json()['incentivized_pools']
list_id_pools = {}
for pool in incentive_pool:
    list_id_pools[pool['pool_id']] = True

print(f'NB POOLS {len(list_id_pools)}')
print('Retrieving informations....')
incentive_pools = dict()
for id_pool in list_id_pools:
    try:
        total_apr = get_pool_apr(id_pool)
        pool_tokens = all_pools[id_pool]
        incentive_pools[pool_tokens] = dict(id_pool=id_pool, total_apr=total_apr)
    except Exception as e:
        print(f'ERREUR / POOL {id_pool}: {e}')


print('... information retrieved!')
i = 0
for pool in dict(sorted(incentive_pools.items(), key=lambda x: x[1]['total_apr'], reverse=True)):
    i += 1
    if  incentive_pools[pool]['id_pool'] in my_pools:
        print(f"===={i}. {pool} {incentive_pools[pool]['total_apr']}")
    else:
        print(f"{i}. {pool} {incentive_pools[pool]['total_apr']}")

print('TOTAL TIME', datetime.datetime.now() - start_time)