from explorer.constants import read_token


class StargazeContract:

    def get_collection(self, collection):
        if collection == 'stars1yw4xvtc43me9scqfr2jr2gzvcxd3a9y4eq7gaukreugw2yd2f8tssqyvcm':
            return 'Colonial Cat'
        print('COLLECTION', collection)
        return collection

    def __init__(self, name):
        self.name = name
        self.type_contract = ''

    def additional_infos(self, message):
        if 'mint' in message['msg']:
            print(message)
            return f"MINT NFT for {read_token(message['funds'][0]['amount'])} STARS"
        if 'claim_mint_nft' in message['msg']:
            return 'CLAIM MINT NFT'
        if 'transfer_nft' in message['msg']:
            print(message)
            transfer = message['msg']['transfer_nft']
            return f"TRANSFER NFT {transfer['token_id']} to {transfer['recipient']}"
        if 'set_bid' in message['msg']:
            bid = message['msg']['set_bid']
            price = read_token(message['funds'][0]['amount'])
            return f"BID {price} STARS FOR COLLECTION {self.get_collection(bid['collection'])} " \
                   f"ID {bid['token_id']}"
        print('MESSAGE', message)
        return ''

    def transaction_name(self, message):
        add_infos = self.additional_infos(message)
        if add_infos and len(add_infos) > 0:
            return self.name + ' : ' + add_infos
        return self.name
