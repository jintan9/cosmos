import requests
import datetime

start_time = datetime.datetime.now()
my_pools = ['1', '560', '578', '601', '604', '606', '611']

def get_pool_infos(id_pool):
    infos = requests.get(f'https://api-osmosis.imperator.co/apr/v1/{id_pool}').json()

    first_apr = infos[0]['apr_list'][0]['apr_14d']
    pool_tokens = id_pool
    if len(infos[0]['apr_list']) == 1:
        # No external incentive
        return pool_tokens, first_apr

    first_symbol = infos[0]['apr_list'][0]['symbol']
    pool_tokens += '_'
    if first_symbol not in ['OSMO', 'ATOM']:
        pool_tokens += first_symbol
    else:
        pool_tokens += infos[0]['apr_list'][1]['symbol']

    total_apr = first_apr + infos[0]['apr_list'][1]['apr_14d']
    print('POOL', id_pool, pool_tokens, total_apr)
    return pool_tokens, total_apr



incentive_pool = requests.get('https://lcd-osmosis.keplr.app/osmosis/pool-incentives/v1beta1/incentivized_pools').json()['incentivized_pools']

list_id_pools = {}
for pool in incentive_pool:
    list_id_pools[pool['pool_id']] = True

print('NB POOLS', len(list_id_pools))
incentive_pools = dict()
for id_pool in list_id_pools:
    pool_tokens, total_apr = get_pool_infos(id_pool)
    incentive_pools[pool_tokens] = dict(id_pool=id_pool, total_apr=total_apr)

for pool in dict(sorted(incentive_pools.items(), key=lambda x: x[1]['total_apr'], reverse=True)):

    if  incentive_pools[pool]['id_pool'] in my_pools:
        print('====', pool, incentive_pools[pool]['total_apr'])
    else:
        print(pool, incentive_pools[pool]['total_apr'])

print('TOTAL TIME', datetime.datetime.now() - start_time)