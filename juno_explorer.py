import argparse

from ibc_model import Juno
from juno_contracts import JunoswapLP, JunoswapPool, Passage, JunoDNS, Fortis, InteractWithToken, \
    DAOToken, OtherJunoContract

ONE_MILLION = 1000 * 1000

parser = argparse.ArgumentParser()
parser.add_argument('--address')
args = parser.parse_args()
juno = Juno(address=args.address)

# https://www.mintscan.io/juno/wasm/contract/juno1hue3dnrtgf9ly2frnnvf8z5u7e224ctc4hk7wks2xumeu3arj6rs9vgzec
list_contracts = dict()
list_contracts['juno1l0z6d7wlwpwequtenwt8pd44685jyhqys6jdnp8xa8ektn0un4zsadyw8y'] = JunoswapLP('LP JUNO UST')
list_contracts['juno1hue3dnrtgf9ly2frnnvf8z5u7e224ctc4hk7wks2xumeu3arj6rs9vgzec'] = JunoswapPool('JUNO UST Pool')
list_contracts['juno18ckrreffz9jwmkw84axsvncexfqt7gpgckskk0yy0vzwm9huqkyq6v78xu'] = JunoswapLP('LP JUNO ATOM')
list_contracts['juno1sg6chmktuhyj4lsrxrrdflem7gsnk4ejv6zkcc4d3vcqulzp55wsf4l4gl'] = JunoswapPool('JUNO ATOM Pool')
list_contracts['juno10mrlcttkwt99wxnqfyk6327lq3ac9yhfle2fd0c5s4rp8dzqy9ps3sjzyf'] = JunoswapPool('JUNO LUNA Pool')
list_contracts['juno1jpdjyc3c973frxkjkmvgr5ececzf9qslzrunxd2xkstem8zr338scnzt27'] = JunoswapLP('LP JUNO STARS')
list_contracts['juno1z5vukf037r6acgln3n37tr8a5rv7wafqzhcq29ddn9etwwtfrytsn6xvux'] = JunoswapPool('JUNO STARS Pool')
list_contracts['juno100pmxfny54wktum5jklg9vme7d5pe44h7va6uw4smccte6wkfaust0untw'] = JunoswapLP('LP JUNO OSMO')
list_contracts['juno1el6rfmz6h9pwpdlf6k2qf4dwt3y5wqd7k3xpyvytklsnkt9uv2aqe8aq4v'] = JunoswapPool('JUNO OSMO Pool')
list_contracts['juno1lgprt38gkp4nvggjl0dm0e7k5lgd80e525f8rjg60tc6fk2xexcqhpp6sm'] = JunoswapLP('LP JUNO HUAHUA')
list_contracts['juno1730cx75d8uevqvrkcwxpy9trhqqfksu5u9xwqss0qe4tn7x0tt3shakhk8'] = JunoswapPool('JUNO HUAHUA Pool')

list_contracts['juno168ctmpyppk90d34p3jjy658zf5a5l3w8wk35wht6ccqj4mr0yv8s4j5awr'] = InteractWithToken('Neta token (action with)')
list_contracts['juno1e8n6ch7msks487ecznyeagmzd5ml2pq9tgedqt2u63vra0q0r9mqrjy6ys'] = JunoswapPool('JUNO NETA Pool')

list_contracts['juno1pshrvuw5ng2q4nwcsuceypjkp48d95gmcgjdxlus2ytm4k5kvz2s7t9ldx'] = InteractWithToken('Hulcat Token')

list_contracts['juno1r4pzw8f9z0sypct5l9j906d47z998ulwvhvqe5xdwgy8wf84583sxwh0pa'] = InteractWithToken('Racoon')
list_contracts['juno1m08vn7klzxh9tmqwajuux202xms2qz3uckle7zvtturcq7vk2yaqpcwxlz'] = JunoswapPool('JUNO RAC Pool')

list_contracts['juno1n4zjxra84uv4wsqd49pcnykfpu2mzrpg8udv5a35jgs952gylasqcnr0rv'] = OtherJunoContract('Doky Drop', token='DOKY')

list_contracts['juno1unjfruscnz39mh42dtekak489s7mnzyh7ry20t80errfkf5j3spqetewaq'] = OtherJunoContract('Claim Marble airdrop', token='MARBLE')
list_contracts['juno1g2g7ucurum66d42g8k5twk34yegdq8c82858gz0tq2fc75zy7khssgnhjl'] = InteractWithToken('Marble')
list_contracts['juno14an9atj9jf77emlrajdcx6a5ykvp4kvwe850w043cp2zf5l2lxlqjh0qs3'] = DAOToken('Old Marble DAO')
list_contracts['juno1ay840g97ngja9k0f9lnywqxwk49245snw69kpwz0ry9qv99q367q3m4x8v'] = DAOToken('Marble DAO')
list_contracts['juno1cvjuc66rdg34guugmxpz6w59rw6ghrun5m33z3hpvx6q60f40knqglhzzx'] = JunoswapPool('JUNO MARBLE Pool')
list_contracts['juno16chnq7j49z289wlhjv3qjzrddz4jf332crz964c8csclydlqxxdqt2ht9t'] = DAOToken('Marble DAO staking')

list_contracts['juno1re3x67ppxap48ygndmrc7har2cnc7tcxtm9nplcas4v0gc3wnmvs3s807z'] = InteractWithToken('HOPE')
list_contracts['juno166nqpdute25frcw5xsg6ax8gj84jcdmsk5grrdecz673pxcjyzlqgnjc0f'] = DAOToken('Hope DAO')
list_contracts['juno18nflutunkth2smnh257sxtxn9p5tq6632kqgsw6h0c02wzpnq9rq927heu'] = JunoswapPool('JUNO HOPE Pool')

list_contracts['juno1vn38rzq0wc7zczp4dhy0h5y5kxh2jjzeahwe30c9cc6dw3lkyk5qn5rmfa'] = InteractWithToken('Cannalab')
list_contracts['juno1k2xzml24sglxlf3hrsmt9a7mtk0jchq279ja5u3asvmtaq3a4uss7xuu5g'] = JunoswapLP('LP JUNO CANNALAB')
list_contracts['juno1acs6q36t6qje5k82h5g74plr258y2q90cjf9z4wnktt7caln0mhsx8mt7z'] = JunoswapPool('JUNO CANNALAB Pool')

list_contracts['juno15le9hmkv67d2hxhm3wdgz9aktnlzrak9ffcckwdqprp26fa4czls5fertz'] = Fortis('Claim Fortis airdrop (get FOT)')
list_contracts['juno1xmpenz0ykxfy8rxr3yc3d4dtqq4dpas4zz3xl6sh873us3vajlpshzp69d'] = Fortis('Burn Fortis (get bFOT)')
list_contracts['juno1vaeuky9hqacenay9nmuualugvv54tdhyt2wsvhnjasx9s946hhmqaq3kh7'] = Fortis('Swap bFOT (get gFOT)')
list_contracts['juno10ynpq4wchr4ruu6mhrfh29495ep4cja5vjnkhz3j5lrgcsap9vtssyeekl'] = Fortis('Stake gFOT')
list_contracts['juno1kh65msgczpzlvat9x94n82v8qnlmtkmjees4pjc9wppckw07d32se6qp6t'] = Fortis('Claim FOT staking rewards')
list_contracts['juno19859m5x8kgepwafc3h0n36kz545ngc2vlqnqxx7gx3t2kguv6fws93cu25'] = JunoswapPool('JUNO bFOT Pool')

list_contracts['juno1uwlazlmh2e7872wg29j2gp6sx5qewtq2qwupfuqfgzq2h4393acs0u9ewu'] = DAOToken('TheDiggers DAO')
list_contracts['juno1s88ymccut9xd4l4ar0v9kf280h35uqtqc6njyry0nv3gysn5mcnqelnfxm'] = DAOToken('TheDiggers Team')

list_contracts['juno1za0uemnhzwkjrqwguy34w45mqdlzfm9hl4s5gp5jtc0e4xvkrwjs6s2rt4'] = Passage('Passage MarketPlace')
list_contracts['juno177m3f78mg5cek8gf5xgea49vs32dt3d6f9dwmuxd3hez3nd7yzgq3ahufw'] = Passage('Passage MarketPlace')

list_contracts['juno1kqx9rhc8ksx52tukdx797k4rjrhkgfh4gljs04ql97hmnnkgyvxs5cqt7d'] = DAOToken('Universe DAO')
list_contracts['juno1mf309nyvr4k4zv0m7m40am9n7nqjf6gupa0wukamwmhgntqj0gxs9hqlrr'] = JunoDNS('Juno DNS')
list_contracts[''] = ''
list_contracts[''] = ''
list_contracts[''] = ''



infos_messages = dict()
infos_messages['/cosmos.staking.v1beta1.MsgDelegate'] = 'Delegate'
infos_messages['/cosmos.staking.v1beta1.MsgBeginRedelegate'] = 'Redelegate'
infos_messages['/cosmos.staking.v1beta1.MsgUndelegate'] = 'Undelegate'
infos_messages['/cosmos.distribution.v1beta1.MsgWithdrawDelegatorReward'] = 'Get Rewards'
infos_messages['/cosmos.authz.v1beta1.MsgGrant'] = 'Grant access (restake)'
infos_messages['/ibc.core.client.v1.MsgUpdateClient'] = 'Update Client'
infos_messages['/ibc.core.channel.v1.MsgAcknowledgement'] = 'Acknowledgement'
infos_messages['/cosmwasm.wasm.v1.MsgInstantiateContract'] = 'Create new contract'

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
    if type_message == '/ibc.applications.transfer.v1.MsgTransfer':
        return f"IBC Transfer to {message['receiver']}"
    if type_message == '/cosmwasm.wasm.v1.MsgExecuteContract':
        try:
            contract = list_contracts[message['contract']]
            contract = contract.transaction_name(message)
        except KeyError:
            contract = 'Unknown contract ' + message['contract']
            print('Unknown message', message)

        return f'Execute contract : {contract}'
    else:
        return f'Unknown type message : {type_message}'


def get_list_messages(tx):
    list_messages = []
    prepend = ''
    if tx['data']['code'] != 0:
        prepend = 'ERROR TRANSACTION : '

    for message in tx['data']['tx']['body']['messages']:
        translated_message = get_type_of_transaction(message)
        if translated_message == 'Execute contract : Hulcat Token (action with)':
            return 'Hulcat Token'
        list_messages.append(translated_message)
    return prepend + ', '.join(list_messages)

nb_tx = 0
first_tx_of_old_batch = -1
last_tx = 0
current_page = 0

while current_page < 4 and first_tx_of_old_batch != last_tx:
    first_tx_of_old_batch = last_tx
    for tx in juno.last_transactions(offset=last_tx):
        print(f"TRANSACTION {tx['data']['timestamp']} {tx['data']['txhash']}")
        print(get_list_messages(tx))
        print()
        nb_tx += 1
        last_tx = tx['header']['id']
    current_page += 1

