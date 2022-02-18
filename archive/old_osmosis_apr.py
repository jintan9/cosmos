import requests

ONE_MILLION = 1000 * 1000
ONE_BILLION = 1000 * 1000 * 1000

APR_REDUCTION = dict()
APR_REDUCTION['14D'] = 1
APR_REDUCTION['7D'] = 1.25  # 80% of APR
APR_REDUCTION['1D'] = 2  # 50% of APR


list_price = requests.get('https://api-osmosis.imperator.co/tokens/v1/all').json()
price_infos = dict()
for token in list_price:
    price_infos[token['name']] = token['price']

print(price_infos)

# incentive_pool = requests.get('https://lcd-osmosis.keplr.app/osmosis/pool-incentives/v1beta1/incentivized_pools').json()['incentivized_pools']
# for pool in incentive_pool:
#    print(pool)

price_osmosis = price_infos['Osmosis']
infos_all_pools = requests.get('https://api-osmosis.imperator.co/search/v1/pools').json()


def osmosis_apr_and_liquidity(info_current_pool, price_osmo, id_gauge, pool_time):
    # Get gauge informations
    gauge = requests.get(
        'https://lcd-osmosis.keplr.app/osmosis/incentives/v1beta1/gauge_by_id/{}'.format(id_gauge)).json()['gauge']

    # How many OSMO still to be earned (in milli_osmo)
    nb_osmo = int(gauge['coins'][0]['amount']) - int(gauge['distributed_coins'][0]['amount'])
    # Pool USD price / why 206 ?
    usd_pool = nb_osmo / 1000 * price_osmo / (206 + 1)
    liquidity = info_current_pool[0]['liquidity']
    volume = info_current_pool[0]['volume_24h']

    # APR = Pool price / liquidity * one year
    apr = usd_pool / (0.99 * liquidity) * 365 * 100
    # If 1D or 7D, % is less
    apr = apr / APR_REDUCTION[pool_time]
    pool_result = dict(liquidity=liquidity, apr=apr, volume=volume)
    return pool_result

def get_total_incentive(list_external_gauges):
    """
    Get how much tokens will be distributed, and the period
    """
    total_nb_tokens = 0
    number_total_epoch = 0
    number_available_epoch = 0
    for id_gauge in list_external_gauges:
        gauge = requests.get(
            'https://lcd-osmosis.keplr.app/osmosis/incentives/v1beta1/gauge_by_id/{}'.format(id_gauge)).json()['gauge']

        total_nb_tokens += int(gauge['coins'][0]['amount']) / ONE_MILLION
        number_total_epoch = int(gauge['num_epochs_paid_over'])
        number_available_epoch = number_total_epoch - int(gauge['filled_epochs'])
    print(total_nb_tokens, number_total_epoch, number_available_epoch)


def get_total_apr(infos_all_pools, price_osmosis, pool_specific):
    """
    Get total APR = Osmosis APR + External APR
    https://twitter.com/StargazeZone/status/1482135175769337856/photo/1
    """
    money_invested = 50
    print('POOL', pool_specific['name_pool'])
    id_gauge = pool_specific['id_gauge']
    id_pool = pool_specific['id_pool']
    pool_time = pool_specific['pool_time']
    pool_result = osmosis_apr_and_liquidity(infos_all_pools[str(id_pool)], price_osmosis,
                                            id_gauge, pool_time)
    print(pool_result)

    # Get number of token/money we get with external incentive
    if pool_specific['epoch_remaining'] > 0:
        nb_tokens_by_day = pool_specific['bonus_total'] / pool_specific['epoch_total']
    else:
        nb_tokens_by_day = 0

    percent_pool = money_invested / pool_result['liquidity']
    osmo_ust_earned = money_invested * pool_result['apr'] / (365 * 100)
    nb_token_earned = percent_pool * nb_tokens_by_day

    total_earned = round((osmo_ust_earned  + nb_token_earned * pool_specific['price_token']) * 365, 2)
    total_apr = round(total_earned / money_invested * 100, 2)
    print('TOTAL', total_earned, 'USD')
    print('TOTAL APR', total_apr, '%')
    print('')
    return dict(apr=round(pool_result['apr'], 2), total_apr=total_apr, total_earned=total_earned,
                liquidity=round(pool_result['liquidity'] / ONE_MILLION, 2))

incentive_pools = dict()
incentive_pools['atom_star_1D'] = dict(id_gauge=1944, bonus_total=5 * ONE_MILLION, epoch_total=90, id_pool=611,
                                       name_pool='ATOM_STAR_1D', epoch_remaining=78, external_gauge=[1998],
                                       price_token=price_infos['Stargaze'], pool_time='1D')
incentive_pools['atom_star_7D'] = dict(id_gauge=1944, bonus_total=15 * ONE_MILLION, epoch_total=90, id_pool=611,
                                       name_pool='ATOM_STAR_7D', epoch_remaining=78, external_gauge=[1998],
                                       price_token=price_infos['Stargaze'], pool_time='7D')
incentive_pools['atom_star'] = dict(id_gauge=1944, bonus_total=30 * ONE_MILLION, epoch_total=90, id_pool=611,
                                    name_pool='ATOM_STAR', epoch_remaining=78, external_gauge=[1998, 1999, 2000],
                                    price_token=price_infos['Stargaze'], pool_time='14D')
incentive_pools['osmo_star'] = dict(id_gauge=1913, bonus_total=30 * ONE_MILLION, epoch_total=90, id_pool=604,
                                    name_pool='OSMO_STAR', epoch_remaining=78,
                                    price_token=price_infos['Stargaze'], pool_time='14D')
incentive_pools['atom_comdex'] = dict(id_gauge=1878, bonus_total=1.5 * ONE_MILLION, epoch_total=90,  id_pool=601,
                                    name_pool='ATOM_CMDX', epoch_remaining=39,
                                    price_token=price_infos['Comdex'], pool_time='14D')
incentive_pools['osmo_comdex'] = dict(id_gauge=1875, bonus_total=1.5 * ONE_MILLION, epoch_total=90, id_pool=600,
                                    name_pool='OSMO_CMDX', epoch_remaining=41,
                                    price_token=price_infos['Comdex'], pool_time='14D')
incentive_pools['osmo_huahua'] = dict(id_gauge=1917, bonus_total=3 * ONE_BILLION, epoch_total=180, id_pool=605,
                                    name_pool='OSMO_HUAHUA', epoch_remaining=169,
                                    price_token=price_infos['Chihuahua'], pool_time='14D')
incentive_pools['atom_huahua'] = dict(id_gauge=1920, bonus_total=3 * ONE_BILLION, epoch_total=180, id_pool=606,
                                      name_pool='ATOM_HUAHUA', epoch_remaining=169,
                                      price_token=price_infos['Chihuahua'], pool_time='14D')
incentive_pools['juno_osmo'] = dict(id_gauge=1509, bonus_total=497224, epoch_total=179, id_pool=497,
                                    name_pool='JUNO_OSMO', epoch_remaining=63,
                                    price_token=price_infos['Juno'], pool_time='14D')

for pool in incentive_pools:
    result = get_total_apr(infos_all_pools, price_osmosis, incentive_pools[pool])
    incentive_pools[pool].update(result)

for pool in dict(sorted(incentive_pools.items(), key=lambda x: x[1]['total_earned'], reverse=True)):
    print(pool, incentive_pools[pool]['total_apr'])



