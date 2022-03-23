
def read_token(number):
    return int(number) / (1000 * 1000)


def read_token_fortis(number):
    return int(number) / (1000 * 1000 * 10000)

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

    def __init__(self, name):
        super().__init__(name)
        self.type_contract = 'Pool'

    def get_token(self):
        # Name is JUNO xx POOL
        infos = self.name.split(' ')
        return infos[0], infos[1]

    def get_output_token(self, swap):
        amm_address = swap['output_amm_address']
        if amm_address == 'juno1hue3dnrtgf9ly2frnnvf8z5u7e224ctc4hk7wks2xumeu3arj6rs9vgzec':
            return 'UST'
        if amm_address == 'juno18nflutunkth2smnh257sxtxn9p5tq6632kqgsw6h0c02wzpnq9rq927heu':
            return 'HOPE'
        if amm_address == 'juno1acs6q36t6qje5k82h5g74plr258y2q90cjf9z4wnktt7caln0mhsx8mt7z':
            return 'CANLAB'
        print('Unknown amm', amm_address)
        return '?'

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
            return f"PASS_SWAP {read_token(swap['input_token_amount'])} " \
                   f"{token_in} for minimum {read_token(swap['output_min_token'])} {self.get_output_token(swap)}"
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

    def additional_infos(self, message):
        pass

class InteractWithToken(JunoContract):

    def __init__(self, name):
        name = name + ' (action with)'
        super().__init__(name)
        self.type_contract = 'action with'

    def additional_infos(self, message):
        pass

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

    def additional_infos(self, message):
        msg = message['msg']
        if 'claim' in msg:
            return f"CLAIM {read_token_fortis(msg['claim']['amount'])} FOT"
        if 'send' in msg:
            return f"SEND {read_token_fortis(msg['send']['amount'])} {self.get_token(message['contract'])}"
        if 'claim_reward' in msg:
            return f"CLAIM REWARD"
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