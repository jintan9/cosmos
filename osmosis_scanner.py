import requests
import argparse
from cosmos_addresses import list_address
parser = argparse.ArgumentParser()
parser.add_argument('--name', choices=[x for x in list_address])
args = parser.parse_args()

def get_price_by_token():
    list_price = requests.get('https://api-osmosis.imperator.co/tokens/v1/all').json()
    price_infos = dict()
    for price_token in list_price:
        price_infos[price_token['name']] = price_token['price']

    list_denom = dict()
    list_denom['uosmo'] = dict(name='OSMO', price=price_infos['Osmosis'])
    list_denom['uion'] = dict(name='ION', price=price_infos['Ion'])
    list_denom['ibc/B547DC9B897E7C3AA5B824696110B8E3D2C31E3ED3F02FF363DCBAD82457E07E'] = dict(
        name='XKI', price=price_infos['Ki'])
    list_denom['ibc/0954E1C28EB7AF5B72D24F3BC2B47BBB2FDF91BDDFD57B74B99E133AED40972A'] = dict(
        name='SCRT', price=price_infos['Secret Network'])
    list_denom['ibc/9BBA9A1C257E971E38C1422780CE6F0B0686F0A3085E2D61118D904BFE0F5F5E'] = dict(
        name='SOMM', price=0)
    list_denom['ibc/0EF15DF2F02480ADE0BB6E85D9EBB5DAEA2836D3860E9F97F9AADE4F57A31AA0'] = dict(
        name='LUNA', price=price_infos['Luna'])
    list_denom['ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2'] = dict(
        name='ATOM', price=price_infos['Cosmos'])
    list_denom['ibc/9712DBB13B9631EDFA9BF61B55F1B2D290B2ADB67E3A4EB3A875F3B6081B3B84'] = dict(
        name='DVPN', price=price_infos['Sentinel'])
    list_denom['ibc/BE1BB42D4BE3C30D50B68D7C41DB4DFCE9678E8EF8C539F6E6A9345048894FCC'] = dict(
        name='UST', price=price_infos['TerraUSD'])
    list_denom['ibc/EA3E1640F9B1532AB129A571203A0B9F789A7F14BB66E350DCBFA18E1A1931F0'] = dict(
        name='CMDX', price=price_infos['Comdex'])
    list_denom['ibc/987C17B11ABC2B20019178ACE62929FE9840202CE79498E29FE8E5CB02B7C0A4'] = dict(
        name='STAR', price=price_infos['Stargaze'])
    list_denom['ibc/EA4C0A9F72E2CEDF10D0E7A9A6A22954DB3444910DB5BE980DF59B05A46DAD1C'] = dict(
        name='DSM', price=price_infos['Desmos'])
    list_denom['ibc/4E5444C35610CC76FC94E7F7886B93121175C28262DDFDDE6F84E82BF2425452'] = dict(
        name='BTSG', price=price_infos['BitSong'])
    list_denom['ibc/46B44899322F3CD854D2D46DEEF881958467CDD4B3B10086DA49296BBED94BED'] = dict(
        name='JUNO', price=price_infos['Juno'])
    list_denom['ibc/B9E0A1A524E98BB407D3CED8720EFEFD186002F90C1B1B7964811DD0CCC12228'] = dict(
        name='HUAHUA', price=price_infos['Chihuahua'])
    list_denom['ibc/7C4D60AA95E5A7558B0A364860979CA34B7FF8AAF255B87AF9E879374470CEC0'] = dict(
        name='IRIS', price=price_infos['IRISnet'])
    return list_denom


prices_by_pool = dict()
prices_by_pool['gamm/pool/1'] = dict(name='OSMO/ATOM', value=1.22)
prices_by_pool['gamm/pool/498'] = dict(name='ATOM/JUNO', value=40.65)
prices_by_pool['gamm/pool/560'] = dict(name='OSMO/UST', value=60.65)
prices_by_pool['gamm/pool/577'] = dict(name='XKI/OSMO', value=1500)
prices_by_pool['gamm/pool/578'] = dict(name='XKI/UST', value=1500)
prices_by_pool['gamm/pool/584'] = dict(name='SCRT/OSMO', value=130)
prices_by_pool['gamm/pool/592'] = dict(name='BTSG/UST', value=100)
prices_by_pool['gamm/pool/601'] = dict(name='OSMO/CDMX', value=329)
prices_by_pool['gamm/pool/604'] = dict(name='OSMO/STAR', value=138600)
prices_by_pool['gamm/pool/605'] = dict(name='HUAHUA/OSMO', value=0.02)
prices_by_pool['gamm/pool/606'] = dict(name='ATOM/HUAHUA', value=0.01)
prices_by_pool['gamm/pool/611'] = dict(name='ATOM/STAR', value=12.71)
prices_by_pool['gamm/pool/619'] = dict(name='DSM/OSMO', value=12)


def get_balance(user_address, price_by_token):
    list_tokens = requests.get('https://lcd-osmosis.keplr.app/bank/balances/' + user_address).json()['result']
    print('')
    for coin in list_tokens:
        try:
            nb_coin = round(int(coin['amount']) / 1000 / 1000, 4)
            print(price_by_token[coin['denom']]['name'], nb_coin,
                  '// ', round(nb_coin * price_by_token[coin['denom']]['price'], 2), 'USD')
        except KeyError:
            print(coin)

def get_pools(user_address, price_by_pool):
    print('POOLS')
    list_lp = requests.get('https://lcd-osmosis.keplr.app/osmosis/lockup/v1beta1/account_locked_coins/' +
                           user_address).json()['coins']
    for lp in sorted(list_lp, key=lambda x:x['denom']):
        nb_lp = round(int(lp['amount']) / (1000 * 1000 * 1000 * 1000 * 1000 * 1000), 4)
        try:
            print('%s (%s) %s LP // %s UST' % (
                lp['denom'], price_by_pool[lp['denom']]['name'], nb_lp,
                round(nb_lp * price_by_pool[lp['denom']]['value'], 2)))
        except KeyError:
            print(lp['denom'], nb_lp)


def get_info_precise(lp, price_by_pool, lock):
    nb_lp = round(int(lp['amount']) / (1000 * 1000 * 1000 * 1000 * 1000 * 1000), 4)

    try:
        price = round(nb_lp * price_by_pool[lp['denom']]['value'], 2)
    except KeyError:
        return lp

    if '86400' in lock['duration']:
        duration = '1 DAY'
    elif '604800' in lock['duration']:
        duration = '7 DAYS'
    else:
        duration = '14 DAYS'

    if lock['end_time'] == '0001-01-01T00:00:00Z':
        return '%s (%s) %s LP // %s UST // LOCK DURATION %s' % (lp['denom'],
                                                                price_by_pool[lp['denom']]['name'],
                                                                nb_lp, price, duration)
    return '%s (%s) %s LP // %s UST // LOCK DURATION %s // END TIME %s' % (
        lp['denom'], price_by_pool[lp['denom']]['name'], nb_lp, price, duration, lock['end_time'])


def get_precise_pools(user_address, price_by_pool):
    print('MORE PRECISE')
    list_locks = requests.get('https://lcd-osmosis.keplr.app/osmosis/lockup/v1beta1/account_locked_longer_duration/' +
                              user_address).json()['locks']
    for lock in sorted(list_locks, key=lambda x: x['coins'][0]['denom']):
        current_lp = lock['coins'][0]
        print(get_info_precise(current_lp, price_by_pool, lock))


address = list_address[args.name]

prices_by_token = get_price_by_token()
get_balance(address, prices_by_token)

get_pools(address, prices_by_pool)
get_precise_pools(address, prices_by_pool)