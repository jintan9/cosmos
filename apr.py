import requests
import datetime
from constants.cosmos_addresses import all_addresses
ONE_MILLION = 1000 * 1000


def get_last_reward(ibc_obj):
    txs = requests.get(ibc_obj.url_last_txs).json()

    for tx in txs:
        if tx['data']['tx']['body']['messages'][0][
            '@type'] == '/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward':
            return tx['data']['timestamp']
    return None

def get_apr(ibc_obj):
    total_delegation = 0
    total_rewards = 0
    delegations = requests.get(ibc_obj.api + 'staking/delegators/' + ibc_obj.address + '/delegations').json()['result']
    for deleg in delegations:
        total_delegation += int(deleg['balance']['amount'])

    rewards = requests.get(ibc_obj.lcd_cosmostation + 'cosmos/distribution/v1beta1/delegators/' + ibc_obj.address + '/rewards').json()['rewards']
    for rew in rewards:
        total_rewards += float(rew['reward'][0]['amount'])

    last_date = get_last_reward(ibc_obj)
    last_date = datetime.datetime.strptime(last_date, '%Y-%m-%dT%H:%M:%SZ')
    last_date -= datetime.timedelta(hours=5)

    nb_hours = (datetime.datetime.now() - last_date).total_seconds() / 3600

    token_per_hour = total_rewards / nb_hours
    token_per_year = token_per_hour * 24 * 365

    apr = token_per_year / total_delegation * 100
    print(ibc_obj.token, 'APR', token_per_year / total_delegation * 100)
    return apr

for ibc_obj in all_addresses:
    get_apr(ibc_obj)