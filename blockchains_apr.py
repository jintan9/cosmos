import requests

def get_json_result(token):
    url = ''
    if token == 'osmo':
        url = 'https://api-osmosis.imperator.co/apr/v2/staking'
    if token == 'nomic':
        url = 'https://app.nomic.io:8443/minting/inflation'

    if url == '':
        return ''
    try:
        return requests.get(url, timeout=3).json()
    except requests.exceptions.ReadTimeout:
        return 'TIMEOUT'

def get_apr(token):
    json_infos = get_json_result(token)
    if token == 'osmo':
        result = float(json_infos)
    if token == 'nomic':
        result = float(json_infos['result']) * 100
    return round(result, 2)

def calculate_apr(api, token, community_tax, inflation=None):
    try:
        pool = requests.get(f'{api}/cosmos/staking/v1beta1/pool', timeout=3).json()['pool']
    except requests.exceptions.ReadTimeout:
        return 'TIMEOUT'
    supply = int(requests.get(f'{api}/cosmos/bank/v1beta1/supply/{token}').json()['amount']['amount'])
    bonded_ratio = int(pool['bonded_tokens']) / supply
    if not inflation:
        inflation = float(requests.get(f'{api}/cosmos/mint/v1beta1/inflation').json()['inflation'])
    return round((inflation * (1 - community_tax)) * 100 / bonded_ratio, 2)

print('ATOM', calculate_apr('https://api.cosmos.network', 'uatom', community_tax=0.02), '%')
print('OSMO', get_apr('osmo'), '%')
print('JUNO', calculate_apr('https://api.juno.omniflix.co', 'ujuno', community_tax=0.02), '%')
print('SCRT', calculate_apr('https://api.scrt.network', 'uscrt', community_tax=0), '%')
print('AKT', calculate_apr('http://135.181.181.122:1518', 'uakt', community_tax=0.02), '%')
print('STARS', calculate_apr('https://api.stars.kingnodes.com', 'ustars', community_tax=0.05, inflation=0.35), '%')
print('HUAHUA', calculate_apr('https://chihuahua-api.mercury-nodes.net', 'uhuahua', community_tax=0.05, inflation=0.43), '%')
print('NOMIC', get_apr('nomic'), '%')

