def read_token(number):
    return round(int(number) / (1000 * 1000), 4)

class StargazeContract:

    def __init__(self, name):
        self.name = name
        self.type_contract = ''

    def additional_infos(self, message):
        if 'mint' in message['msg']:
            return f"MINT NFT for {read_token(message['funds'][0]['amount'])} STARS"
        if 'claim_mint_nft' in message['msg']:
            return 'CLAIM MINT NFT'
        if 'transfer_nft' in message['msg']:
            transfer = message['msg']['transfer_nft']
            return f"TRANSFER NFT {transfer['token_id']} to {transfer['recipient']}"
        print('MESSAGE', message)
        return ''

    def transaction_name(self, message):
        add_infos = self.additional_infos(message)
        if add_infos and len(add_infos) > 0:
            return self.name + ' : ' + add_infos
        return self.name
