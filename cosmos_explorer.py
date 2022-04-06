import argparse
import datetime

from ibc_model import Juno, Osmo, ATOM, Stargaze, Secret, Sifchain, Crescent
from juno_contracts_model import list_contracts

ONE_MILLION = 1000 * 1000

parser = argparse.ArgumentParser()
parser.add_argument('--address')
parser.add_argument('--pages', default=1)
args = parser.parse_args()

def get_ibc_chain(address):
    if address.startswith('osmo'):
        return Osmo(address=address)
    if address.startswith('juno'):
        return Juno(address=address)
    if address.startswith('cosmos'):
        return ATOM(address=address)
    if address.startswith('stars'):
        return Stargaze(address=address)
    if address.startswith('secret'):
        return Secret(address=address)
    if address.startswith('sif'):
        return Sifchain(address=address)
    if address.startswith('cre'):
        return Crescent(address=address)

ibc_address = get_ibc_chain(address=args.address)


infos_messages = dict()
infos_messages['/cosmos.staking.v1beta1.MsgDelegate'] = 'Delegate'
infos_messages['/cosmos.staking.v1beta1.MsgBeginRedelegate'] = 'Redelegate'
infos_messages['/cosmos.staking.v1beta1.MsgUndelegate'] = 'Undelegate'
infos_messages['/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward'] = 'Get Rewards'
infos_messages['/cosmos.authz.v1beta1.MsgGrant'] = 'Grant access (restake)'
infos_messages['/ibc.core.client.v1.MsgUpdateClient'] = 'Update Client'
infos_messages['/ibc.core.channel.v1.MsgAcknowledgement'] = 'Acknowledgement'
infos_messages['/cosmwasm.wasm.v1.MsgInstantiateContract'] = 'Create new contract'
infos_messages['/osmosis.lockup.MsgBeginUnlocking'] = 'Unlocking LP'
infos_messages['/osmosis.superfluid.MsgSuperfluidDelegate'] = 'Superfluid Staking'

def get_type_of_transaction(message):
    type_message = message['@type']
    if type_message in infos_messages:
        return infos_messages[type_message]
    if type_message == '/cosmos.gov.v1beta1.MsgVote':
        return f"Vote for proposal {message['proposal_id']} : {message['option']}"
    if type_message == '/cosmos.bank.v1beta1.MsgSend':
        return f"IBC Sent to {message['to_address']}"
    if type_message == '/ibc.core.channel.v1.MsgRecvPacket':
        return f"IBC Received"
    if type_message == '/osmosis.gamm.v1beta1.MsgSwapExactAmountIn':
        print(message)
        return 'SWAP'
    if type_message == '/osmosis.gamm.v1beta1.MsgJoinPool':
        return f"JOIN LP {message['poolId']}"
    if type_message == '/osmosis.lockup.MsgLockTokens':
        return f"LOCK LP {message['coins'][0]['denom']} FOR {int(message['duration'][:-1]) / 86400} DAYS"
    if type_message == '/ibc.applications.transfer.v1.MsgTransfer':
        return f"IBC Transfer to {message['receiver']}"
    if type_message == '/cosmwasm.wasm.v1.MsgExecuteContract':
        try:
            contract = list_contracts[message['contract']]
            contract = contract.transaction_name(message)
        except KeyError as e:
            print('KEY ERROR', e)
            contract = 'Unknown contract ' + message['contract']
            print('Unknown message', message)

        return f'Execute contract : {contract}'
    else:
        return f'Unknown type message : {type_message}'


def get_list_messages(tx_dict):
    list_messages = []
    prepend = ''
    if tx_dict['data']['code'] != 0:
        prepend = 'ERROR TRANSACTION : '

    for message in tx_dict['data']['tx']['body']['messages']:
        translated_message = get_type_of_transaction(message)
        if 'Hulcat Token (action with) : TRANSFER' in translated_message:
            return 'Hulcat Token'
        list_messages.append(translated_message)
    return prepend + ', '.join(list_messages)

nb_tx = 0
first_tx_of_old_batch = -1
last_tx = 0
current_page = 0

print('LOGS FOR', ibc_address.address, 'DATE', datetime.datetime.now())
print('')
while current_page < int(args.pages) and first_tx_of_old_batch != last_tx:
    first_tx_of_old_batch = last_tx
    for tx in ibc_address.last_transactions(offset=last_tx):
        print(f"TRANSACTION {tx['data']['timestamp']} {tx['data']['txhash']}")
        print(get_list_messages(tx))
        print()
        nb_tx += 1
        last_tx = tx['header']['id']
    current_page += 1

