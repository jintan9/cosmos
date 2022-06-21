from explorer.constants import read_token, read_token_rowan


def coin_name(denom):
    if denom == 'ibc/27394FB092D2ECCD56123C74F36E4C1F926001CEADA9CA97EA622B25F41E5EB2':
        return 'ATOM'
    if denom == 'ibc/B4314D0E670CB43C88A5DCA09F76E5E812BD831CC2FEC6E434C9E5A9D1F57953':
        return 'OSMO'
    return denom

def readable_figure(coin, number):
    if coin == 'rowan':
        return read_token_rowan(number)
    return read_token(number)

def get_sif_transaction(type_message, message):
    if type_message == '/sifnode.clp.v1.MsgSwap':
        token_in = coin_name(message['sent_asset']['symbol'])
        token_out = coin_name(message['received_asset']['symbol'])
        amount_in = readable_figure(token_in, message['sent_amount'])
        amount_out = readable_figure(token_out, message['min_receiving_amount'])
        return f"SWAP {amount_in} {token_in} for min {amount_out} {token_out}"
    if type_message == '/sifnode.clp.v1.MsgRemoveLiquidity':
        print('MESSAGE', message)
        return f"REMOVE LIQUIDITY for {coin_name(message['external_asset']['symbol'])}"
    if type_message == '/sifnode.clp.v1.MsgAddLiquidity':
        token_1 = 'rowan'
        token_2 = coin_name(message['external_asset']['symbol'])
        amount_1 = readable_figure(token_1, message['native_asset_amount'])
        amount_2 = readable_figure(token_2, message['external_asset_amount'])
        return f"ADD LIQUIDITY : {amount_1} {token_1} and {amount_2} {token_2}"
    if type_message == '/sifnode.clp.v1.MsgUnlockLiquidityRequest':
        print('MESSAGE', message)
        token_2 = coin_name(message['external_asset']['symbol'])
        return f'START UNLOCK LIQUIDITY FOR {token_2}'
    print(type_message)
    print(message)
    return 'SIF'