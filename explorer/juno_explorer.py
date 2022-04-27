
def read_token(number):
    return round(int(number) / (1000 * 1000), 4)


def read_token_fortis(number):
    return round(int(number) / (1000 * 1000 * 10000), 4)

class JunoContract:

    def __init__(self, name):
        self.name = name
        self.type_contract = ''

    def additional_infos(self, message):
        print(message)
        return ''

    def transaction_name(self, message):
        add_infos = self.additional_infos(message)
        if add_infos and len(add_infos) > 0:
            return self.name + ' : ' + add_infos
        return self.name


class JunoswapPool(JunoContract):

    @classmethod
    def get_output_token(cls, amm_address):
        adresses = dict()
        adresses['juno1hue3dnrtgf9ly2frnnvf8z5u7e224ctc4hk7wks2xumeu3arj6rs9vgzec'] = 'UST'
        adresses['juno1sg6chmktuhyj4lsrxrrdflem7gsnk4ejv6zkcc4d3vcqulzp55wsf4l4gl'] = 'ATOM'
        adresses['juno10mrlcttkwt99wxnqfyk6327lq3ac9yhfle2fd0c5s4rp8dzqy9ps3sjzyf'] = 'LUNA'
        adresses['juno1z5vukf037r6acgln3n37tr8a5rv7wafqzhcq29ddn9etwwtfrytsn6xvux'] = 'STARS'
        adresses['juno1el6rfmz6h9pwpdlf6k2qf4dwt3y5wqd7k3xpyvytklsnkt9uv2aqe8aq4v'] = 'OSMO'
        adresses['juno1730cx75d8uevqvrkcwxpy9trhqqfksu5u9xwqss0qe4tn7x0tt3shakhk8'] = 'HUAHUA'
        adresses['juno18nflutunkth2smnh257sxtxn9p5tq6632kqgsw6h0c02wzpnq9rq927heu'] = 'HOPE'
        adresses['juno1acs6q36t6qje5k82h5g74plr258y2q90cjf9z4wnktt7caln0mhsx8mt7z'] = 'CANLAB'
        adresses['juno1hkz5dhn59w6l29k8w8ceuramqx2f35qpen7xtlx6ezketwh8ndxq8rwq2a'] = 'SCRT'
        adresses['juno1tmxx3rdnnrcckkh7pjde924lftjs724rzd44sqte5xh8xax0yf2sc7v7dk'] = 'AKT'
        adresses['juno152lfpmadpxh2xha5wmlh2np5rj8fuy06sk72j55v686wd4q4c9jsvwj0gm'] = 'CMDX'
        try:
            return adresses[amm_address]
        except KeyError as e:
            print('Unknown AMM', e)
            return '?'

    def __init__(self, name, multiple=1):
        super().__init__(name)
        self.type_contract = 'Pool'
        self.multiple = multiple

    def get_token(self):
        # Name is JUNO xx POOL
        infos = self.name.split(' ')
        return infos[0], infos[1]

    def additional_infos(self, message):
        msg = message['msg']
        token1, token2 = self.get_token()
        if 'swap' in msg:
            swap = msg['swap']
            token_in = token1 if swap['input_token'] == 'Token1' else token2
            token_out = token2 if swap['input_token'] == 'Token1' else token1
            return f"SWAP {read_token(int(swap['input_amount']))} " \
                   f"{token_in} for minimum {read_token(int(swap['min_output']))} {token_out}"
        if 'pass_through_swap' in msg:
            swap = msg['pass_through_swap']
            token_in = token1 if swap['input_token'] == 'Token1' else token2
            token_out = token2 if swap['input_token'] == 'Token1' else token1
            return f"PASS_SWAP {read_token(swap['input_token_amount']) / self.multiple} " \
                   f"{token_in} for minimum {read_token(swap['output_min_token'])} {self.get_output_token(swap['output_amm_address'])}"
        if 'add_liquidity' in msg:
            liqui = msg['add_liquidity']
            return f"ADD LIQUIDITY {read_token(liqui['token1_amount'])} {token1} and " \
                   f"{read_token(liqui['max_token2'])} {token2}"
        if 'remove_liquidity' in msg:
            liqui = msg['remove_liquidity']
            return f"REMOVE LIQUIDITY {read_token(liqui['amount'])}"
        print('Unknown pool', message)
        return ''


class JunoswapLP(JunoContract):

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'LP'
        self.name = name

    def get_readable_contrat(self, contract):
        if contract == 'juno1vc5rx2le4y98mvaa27arstyd8ujgmdpdkm5hgltkk8vfwjh6j3mqcqj8qd':
            return 'SFOT BFOT'
        if contract == 'juno1w9xdfr8j47209dae5t3l37g8qp2y67z4dgnrfd43040u7uvwnp3s6p89s4':
            return 'SFOT UST'
        if contract == 'juno1umd7k0nrnjjqj2cuu3aclfjcfje4hvdehq2a309g6ery0fjhwf9sh6geq8':
            return 'SFOT GFOT'
        print('Unknown readable contract', contract)
        return contract

    def additional_infos(self, message):
        msg = message['msg']
        if 'send' in msg:
            return f"SEND {read_token(msg['send']['amount'])} TO GET LP {self.get_readable_contrat(msg['send']['contract'])}"
        if 'increase_allowance' in msg:
            return ''
        print('Unknown LP', message['msg'])

class InteractWithToken(JunoContract):

    def __init__(self, name):
        name = name + ' (action with)'
        super().__init__(name)
        self.type_contract = 'action with'

    def additional_infos(self, message):
        msg = message['msg']
        if 'increase_allowance' in msg:
            return ''
        if 'send' in msg:
            return f"SEND {read_token(msg['send']['amount'])} TO {msg['send']['contract']}"
        if 'transfer' in msg:
            return f"TRANSFER {read_token(msg['transfer']['amount'])} TO {msg['transfer']['recipient']}"
        print('Unkwown Interact', msg)
        return ''

class OtherJunoContract(JunoContract):

    def __init__(self, name, token):
        super().__init__(name)
        self.type_contract = 'other contract'
        self.token = token

    def additional_infos(self, message):
        msg = message['msg']
        if 'claim' in msg:
            return f"CLAIM {read_token(msg['claim']['amount'])} {self.token}"
        print('Unknown other contract', message)
        return ''

class DAOToken(JunoContract):

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'DAO DAO'

    def additional_infos(self, message):
        msg = message['msg']
        if 'vote' in msg:
            return f"VOTE for proposal {msg['vote']['proposal_id']} : {msg['vote']['vote']}"
        if 'unstake' in msg:
            return f"UNSTAKE {msg['unstake']['amount']}"
        if 'unstake' in msg:
            return f"UNSTAKE {msg['unstake']['amount']}"
        if 'propose' in msg:
            return f"PROPOSE VOTE : {msg['propose']['title']}"
        if 'execute' in msg:
            return f"EXECUTE : {msg['execute']['proposal_id']}"
        if 'transfer' in msg:
            return f"TRANSFER {read_token(msg['transfer']['amount'])} TOKEN TO {msg['transfer']['recipient']} "
        if 'claim' in msg:
            print(msg)
            return f"CLAIM"
        if 'send' in msg:
            return f"SEND TO {msg['send']['owner']}"
        print('Unknown DAO', message)
        return ''

class Fortis(JunoContract):

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'fortis'

    def get_token(self, contract):
        if contract == 'juno1vaeuky9hqacenay9nmuualugvv54tdhyt2wsvhnjasx9s946hhmqaq3kh7':
            return 'bFOT'
        if contract == 'juno10ynpq4wchr4ruu6mhrfh29495ep4cja5vjnkhz3j5lrgcsap9vtssyeekl':
            return 'gFOT'
        if contract == 'juno1xmpenz0ykxfy8rxr3yc3d4dtqq4dpas4zz3xl6sh873us3vajlpshzp69d':
            return 'FOT'
        print('Unknown contract', contract)
        return 'FOT'

    def get_readable_contrat(self, contract):
        if contract == 'juno1vetgykcprr7hwe3uplhy84xhc4yshr6q0nnvg28wxjrdnuvwa7dqvv20ss':
            return 'GET BFOT'
        if contract == 'juno1gvk3pcpkkggmhgwe0tk0rnc4qcnqkxh9djte95tjwqdwyxcd8ztsp9tcs4':
            return 'GET GFOT'
        if contract == 'juno1rx8vrczpucvmrrymrdsmtj5500wpgk8y9kry472sp6mx3gduusuqkvjmt0':
            return 'STAKE GFOT'
        if contract == 'juno1tyw3kx4y9nt6gxjvg9pw9hcjqgtf6gmw7g8g0u8uyfww66y5lv7qppw7uz':
            return 'STAKE GFOT'
        if contract == 'juno1xu5nm2n7drr6hmjvy6l88n2u5kve8hay3x5djls4ee2x9dxzfn8q7w2awm':
            return 'STAKE LP POOL3'
        if contract == 'juno1v930newf9rruwrg989hc732fkr5h8uq3ta6t3pnxne0ugf0ff9asyyp4ss':
            return 'STAKE LP POOL8'
        print('Unknown Fortis readable contract', contract)
        return contract

    def additional_infos(self, message):
        msg = message['msg']
        if 'claim' in msg:
            return f"CLAIM {read_token_fortis(msg['claim']['amount'])} FOT"
        if 'send' in msg:
            return f"SEND {read_token_fortis(msg['send']['amount'])} TO {self.get_readable_contrat(msg['send']['contract'])}"
        if 'claim_reward' in msg:
            return f"CLAIM REWARD"
        if 'swap' in msg:
            token1, token2 = 'Token1', 'Token2'
            swap = msg['swap']
            token_in = token1 if swap['input_token'] == 'Token1' else token2
            token_out = token2 if swap['input_token'] == 'Token1' else token1
            return f"SWAP {read_token(int(swap['input_amount']))} " \
                   f"{token_in} for minimum {read_token(int(swap['min_output']))} {token_out}"
        if 'add_liquidity' in msg:
            token1, token2 = 'Token1', 'Token2'
            liqui = msg['add_liquidity']
            return f"ADD LIQUIDITY {read_token(liqui['token1_amount'])} {token1} and " \
                   f"{read_token(liqui['max_token2'])} {token2}"
        if 'increase_allowance' in msg:
            return ''
        if 'create_unstake' in msg:
            return f"UNSTAKE {read_token_fortis(msg['create_unstake']['unstake_amount'])} gFOT"
        if 'fetch_unstake' in msg:
            return f"FETCH UNSTAKE"
        if 'transfer' in msg:
            return f"TRANSFER {read_token_fortis(msg['transfer']['amount'])} TO {msg['transfer']['recipient']}"
        print('Unknown Fortis', msg)
        return ''

class Passage(JunoContract):

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'passage'

    def additional_infos(self, message):
        msg = message['msg']
        if 'approve' in msg:
            return f"APPROVE {msg['approve']['token_id']}"
        if 'update_price' in msg:
            return f"UPDATE PRICE : {read_token(msg['update_price']['price'])} ATOM FOR {msg['update_price']['token']}"
        if 'list_tokens' in msg:
            infos = ''
            for token in msg['list_tokens']['tokens']:
                infos += f"LIST TOKEN {token['id']} for {read_token(token['price'])} ATOM"
            return infos
        if 'delist_tokens' in msg:
            return f"DELIST TOKEN {msg['delist_tokens']['tokens']}"
        if 'buy' in msg:
            return f"BUY {msg['buy']['token_id']} for {read_token(message['funds'][0]['amount'])} ATOM"
        print('Unknown Passage', message)
        return ''

class JunoDNS(JunoContract):

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'passage'

    def additional_infos(self, message):
        msg = message['msg']
        if 'mint' in msg:
            return f"MINT {msg['mint']['token_id']} DNS"
        print('Unknown DNS', message)
        return ''


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
list_contracts['juno1tmxx3rdnnrcckkh7pjde924lftjs724rzd44sqte5xh8xax0yf2sc7v7dk'] = JunoswapPool('JUNO AKT Pool')
list_contracts['juno1j7pdtemw0qvl6rmnl0sf324409gz2p4sdt6rv659482x9rqqz6mqd653dg'] = JunoswapPool('JUNO BTSG Pool')
list_contracts['juno18hu00pwvd8kq0cgzk03l2nmp8rr0h5gp6tektz6qazwfapqsl4cqwfgdsv'] = JunoswapLP('LP JUNO BTSG')
list_contracts['juno1hkz5dhn59w6l29k8w8ceuramqx2f35qpen7xtlx6ezketwh8ndxq8rwq2a'] = JunoswapPool('JUNO SCRT Pool')

list_contracts['juno152lfpmadpxh2xha5wmlh2np5rj8fuy06sk72j55v686wd4q4c9jsvwj0gm'] = JunoswapPool('JUNO CMDX Pool')

list_contracts['juno168ctmpyppk90d34p3jjy658zf5a5l3w8wk35wht6ccqj4mr0yv8s4j5awr'] = InteractWithToken('Neta token')
list_contracts['juno1jmechmr7w6kwqu8jcy5973rtllxgttyetarys60rtsu0g675mkjsy96t8l'] = JunoswapLP('LP JUNO NETA')
list_contracts['juno1e8n6ch7msks487ecznyeagmzd5ml2pq9tgedqt2u63vra0q0r9mqrjy6ys'] = JunoswapPool('JUNO NETA Pool')

list_contracts['juno1pshrvuw5ng2q4nwcsuceypjkp48d95gmcgjdxlus2ytm4k5kvz2s7t9ldx'] = InteractWithToken('Hulcat Token')

list_contracts['juno1r4pzw8f9z0sypct5l9j906d47z998ulwvhvqe5xdwgy8wf84583sxwh0pa'] = InteractWithToken('Racoon')
list_contracts['juno1m08vn7klzxh9tmqwajuux202xms2qz3uckle7zvtturcq7vk2yaqpcwxlz'] = JunoswapPool('JUNO RAC Pool')

list_contracts['juno1n4zjxra84uv4wsqd49pcnykfpu2mzrpg8udv5a35jgs952gylasqcnr0rv'] = OtherJunoContract('Doky Drop', token='DOKY')
list_contracts['juno1svqmj8cgmqwza6a7dxvpt3tew0ggynuzxepuw4p5vgts4epfzfwspz3ylw'] = OtherJunoContract('Claim Neta airdrop', token='NETA')
list_contracts['juno1unjfruscnz39mh42dtekak489s7mnzyh7ry20t80errfkf5j3spqetewaq'] = OtherJunoContract('Claim Marble airdrop', token='MARBLE')
list_contracts['juno1xd02gdprk20wr4d2ayk8nuwh4yupfz66hwc2yp9q8kvludr5x62s4czeav'] = OtherJunoContract('Claim Block airdrop', token='BLOCK')

list_contracts['juno1g2g7ucurum66d42g8k5twk34yegdq8c82858gz0tq2fc75zy7khssgnhjl'] = InteractWithToken('Marble')
list_contracts['juno14an9atj9jf77emlrajdcx6a5ykvp4kvwe850w043cp2zf5l2lxlqjh0qs3'] = DAOToken('Old Marble DAO')
list_contracts['juno1ay840g97ngja9k0f9lnywqxwk49245snw69kpwz0ry9qv99q367q3m4x8v'] = DAOToken('Marble DAO')
list_contracts['juno1cvjuc66rdg34guugmxpz6w59rw6ghrun5m33z3hpvx6q60f40knqglhzzx'] = JunoswapPool('JUNO MARBLE Pool')
list_contracts['juno16chnq7j49z289wlhjv3qjzrddz4jf332crz964c8csclydlqxxdqt2ht9t'] = DAOToken('Marble DAO staking')
list_contracts['juno1y9rf7ql6ffwkv02hsgd4yruz23pn4w97p75e2slsnkm0mnamhzysvqnxaq'] = InteractWithToken('Block')
list_contracts['juno1xf32js0lc6v7quxj5twuna97hwff7dhkz6psujavvknh2yzty5uq6wut8j'] = JunoswapPool('BLOCK JUNO Pool')

list_contracts['juno1re3x67ppxap48ygndmrc7har2cnc7tcxtm9nplcas4v0gc3wnmvs3s807z'] = InteractWithToken('HOPE')
list_contracts['juno166nqpdute25frcw5xsg6ax8gj84jcdmsk5grrdecz673pxcjyzlqgnjc0f'] = DAOToken('Hope DAO')
list_contracts['juno17w75xxt0uxc8tsrcdtdkx9xgvspkzt7p5fz07lec4azjudnrjvcqhnr2kk'] = JunoswapLP('LP JUNO HOPE')
list_contracts['juno18nflutunkth2smnh257sxtxn9p5tq6632kqgsw6h0c02wzpnq9rq927heu'] = JunoswapPool('JUNO HOPE Pool')

list_contracts['juno1vn38rzq0wc7zczp4dhy0h5y5kxh2jjzeahwe30c9cc6dw3lkyk5qn5rmfa'] = InteractWithToken('Cannalab')
list_contracts['juno1k2xzml24sglxlf3hrsmt9a7mtk0jchq279ja5u3asvmtaq3a4uss7xuu5g'] = JunoswapLP('LP JUNO CANNALAB')
list_contracts['juno1acs6q36t6qje5k82h5g74plr258y2q90cjf9z4wnktt7caln0mhsx8mt7z'] = JunoswapPool('JUNO CANNALAB Pool')

list_contracts['juno15le9hmkv67d2hxhm3wdgz9aktnlzrak9ffcckwdqprp26fa4czls5fertz'] = Fortis('Claim Fortis airdrop (get FOT)')
list_contracts['juno1xmpenz0ykxfy8rxr3yc3d4dtqq4dpas4zz3xl6sh873us3vajlpshzp69d'] = Fortis('Burn Fortis (get bFOT)')
list_contracts['juno1vaeuky9hqacenay9nmuualugvv54tdhyt2wsvhnjasx9s946hhmqaq3kh7'] = Fortis('Swap bFOT (get gFOT)')
list_contracts['juno10ynpq4wchr4ruu6mhrfh29495ep4cja5vjnkhz3j5lrgcsap9vtssyeekl'] = Fortis('Stake gFOT')
list_contracts['juno1kh65msgczpzlvat9x94n82v8qnlmtkmjees4pjc9wppckw07d32se6qp6t'] = Fortis('Claim FOT staking rewards')
list_contracts['juno1s3073d0746dmcy4fwf83fwm9yuwp5rcgls65capfhxzunzlv8gfssl47v0'] = Fortis('Claim Fortis airdrop for JUNO')
list_contracts['juno1tyw3kx4y9nt6gxjvg9pw9hcjqgtf6gmw7g8g0u8uyfww66y5lv7qppw7uz'] = Fortis('Update GFOT Staking')
list_contracts['juno17c7zyezg3m8p2tf9hqgue9jhahvle70d59e8j9nmrvhw9anrpk8qxlrghx'] = Fortis('Stable SFOT')
list_contracts['juno1vc5rx2le4y98mvaa27arstyd8ujgmdpdkm5hgltkk8vfwjh6j3mqcqj8qd'] = Fortis('SFOT BFOT Fortis')
list_contracts['juno1umd7k0nrnjjqj2cuu3aclfjcfje4hvdehq2a309g6ery0fjhwf9sh6geq8'] = Fortis('SFOT GFOT Fortis')
list_contracts['juno1w9xdfr8j47209dae5t3l37g8qp2y67z4dgnrfd43040u7uvwnp3s6p89s4'] = Fortis('SFOT UST Fortis')


list_contracts['juno1xu5nm2n7drr6hmjvy6l88n2u5kve8hay3x5djls4ee2x9dxzfn8q7w2awm'] = Fortis('Dungeon Pool 3 LP Staking')
list_contracts['juno1p4y3la4h4ckmsndsgrhvs90f2vtsw8t3edehj39dup768r5087nsmt6kzc'] = Fortis('LP POOL2')
list_contracts['juno14wh95tv40z5jd76ppxv08jzpqr2lfvujl9tvxj0zac5tx3sfjdqqvuzs5t'] = Fortis('POOL2')
list_contracts['juno13kys802wnpzlyp57uyua3zaa0uvmkv0ytmcjqsax8ea3cysm2wyqsxnxn3'] = Fortis('LP POOL3')
list_contracts['juno1t5uhk3s34jy322ps4z4ffwmzs2zraqh8whv2fze20kq6avclpu4qgdswq5'] = Fortis('POOL3')
list_contracts['juno1lyg9wwjc4psrh6u7c5ummt4er6uzuztd345wmrr7xwrk4amrwkwq2vd2ws'] = Fortis('POOL8')

list_contracts['juno1v930newf9rruwrg989hc732fkr5h8uq3ta6t3pnxne0ugf0ff9asyyp4ss'] = Fortis('Dungeon Pool 8')
list_contracts['juno1f3tfeaz6qnq8r3n3xfsde0r7c20z7k9w0rpzustp7y6y2x3st2hs4yvqjn'] = Fortis('LP2 ??')
list_contracts['juno1s494eeq9vx596p39na5gqxgjzgn07jgg87940w6y3ap99qvdn95qftzgh6'] = Fortis('LP POOL8')
list_contracts['juno1wjpdhpv7x5cusg028xglazr8ldxr7cnm0tss8sd9pg4r959rlgtqjkf70x'] = Fortis('SFOT ATOM')
list_contracts['juno1wuu8nwr37kmg0njg6p3ag7j4qcm08vs6z9e9j28aendnfnuxmd3sc4yrhm'] = Fortis('SFOT JUNO')

list_contracts['juno1te6t7zar4jrme4re7za0vzxf72rjkwwzxrksu83505l89gdzcy9sd93v4c'] = JunoswapLP('LP SFOT UST')
list_contracts['juno1qg9m2zdqaxx4udxxyun4cjq5myazlldymdmhkuy7fmvretyxz92q89zdvv'] = JunoswapPool('SFOT UST Pool')
list_contracts['juno19qetspgghczk5hvw3su602vjqqdhgl062eftgh897cdka6lny5sq6yhmg4'] = JunoswapLP('LP SFOT BFOT')
list_contracts['juno1dug89d22vtu7v27ee9gg4xq5seu2tu705d6eh3kmvh0uvy7depaqg45qdj'] = JunoswapPool('SFOT BFOT Pool')
list_contracts['juno129xs226p0lqtdmkca7p27ajc6y8lv3xqgx9mzzyueazd8fzd8y6svnvu4q'] = JunoswapLP('LP SFOT GFOT')
list_contracts['juno1r72th8l800djmhu8f0xhfkw046a4zlm0kcrela2vxwf0ehh3l68qumh53q'] = JunoswapPool('SFOT GFOT Pool')


list_contracts['juno19859m5x8kgepwafc3h0n36kz545ngc2vlqnqxx7gx3t2kguv6fws93cu25'] = JunoswapPool('JUNO bFOT Pool', multiple=10000)

list_contracts['juno1uwlazlmh2e7872wg29j2gp6sx5qewtq2qwupfuqfgzq2h4393acs0u9ewu'] = DAOToken('TheDiggers DAO')
list_contracts['juno1s88ymccut9xd4l4ar0v9kf280h35uqtqc6njyry0nv3gysn5mcnqelnfxm'] = DAOToken('TheDiggers Team')

list_contracts['juno1za0uemnhzwkjrqwguy34w45mqdlzfm9hl4s5gp5jtc0e4xvkrwjs6s2rt4'] = Passage('Passage MarketPlace')
list_contracts['juno177m3f78mg5cek8gf5xgea49vs32dt3d6f9dwmuxd3hez3nd7yzgq3ahufw'] = Passage('Passage MarketPlace')

list_contracts['juno1kqx9rhc8ksx52tukdx797k4rjrhkgfh4gljs04ql97hmnnkgyvxs5cqt7d'] = DAOToken('Universe DAO')
list_contracts['juno1mf309nyvr4k4zv0m7m40am9n7nqjf6gupa0wukamwmhgntqj0gxs9hqlrr'] = JunoDNS('Juno DNS')
list_contracts[''] = ''
