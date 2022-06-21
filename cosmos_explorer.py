import argparse
import datetime

from explorer.crescent_explorer import get_crescent_transaction
from explorer.osmosis_explorer import get_osmosis_transaction
from explorer.sif_explorer import get_sif_transaction
from ibc_model import Juno, Osmo, ATOM, Stargaze, Sifchain, Crescent
from explorer.juno_explorer import list_contracts as juno_contracts
from explorer.stargaze_explorer import StargazeContract

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
    if address.startswith('sif'):
        return Sifchain(address=address)
    if address.startswith('cre'):
        return Crescent(address=address)
    raise Exception('Chain not supported')

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


def get_cosmos_address(address):
    if address == 'cosmos15v50ymp6n5dn73erkqtmq0u8adpl8d3ujv2e74':
        return f'Binance ({address})'
    if address == 'cosmos1psr5x3kgra5fvm4gc4l6ufykn0nl3esdjeex8n':
        return f'Exchange1 ({address})'
    if address == 'cosmos18ld4633yswcyjdklej3att6aw93nhlf7ce4v8u':
        return f'Exchange2 ({address})'
    if address == 'cosmos1gwyv83zcnckdhuz3n78rvyzj59u8x6l8dk9cfy':
        return f'Exchange3 ({address})'
    if address == 'cosmos17muvdgkep4ndptnyg38eufxsssq8jr3wnkysy8':
        return f'Kucoin ({address})'
    if address == ibc_address.address:
        return 'me'
    return address


def get_type_of_transaction(message):
    type_message = message['@type']
    if type_message in infos_messages:
        return infos_messages[type_message]
    if type_message == '/cosmos.gov.v1beta1.MsgVote':
        return f"Vote for proposal {message['proposal_id']} : {message['option']}"
    if type_message == '/cosmos.bank.v1beta1.MsgSend':
        return f"IBC Transfer : from {get_cosmos_address(message['from_address'])} to " \
               f"{get_cosmos_address(message['to_address'])}"
    if type_message == '/ibc.core.channel.v1.MsgRecvPacket':
        return f"IBC Received"
    if type_message.startswith('/crescent'):
        return get_crescent_transaction(type_message, message)
    if type_message.startswith('/sifnode'):
        return get_sif_transaction(type_message, message)
    if type_message.startswith('/osmosis'):
        return get_osmosis_transaction(type_message, message)
    if type_message == '/ibc.applications.transfer.v1.MsgTransfer':
        return f"IBC Transfer to {message['receiver']}"
    if type_message == '/cosmwasm.wasm.v1.MsgExecuteContract':
        if type(ibc_address) == Juno:
            try:
                contract = juno_contracts[message['contract']]
                contract = contract.transaction_name(message)
            except KeyError as e:
                print('KEY ERROR', e)
                contract = 'Unknown contract ' + message['contract']
                print('Unknown message', message)
        if type(ibc_address) == Stargaze:
            contract = StargazeContract('STARGAZE')
            contract = contract.transaction_name(message)

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

