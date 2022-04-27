def read_token(number):
    return round(int(number) / (1000 * 1000), 4)

def read_big_token(number):
    return round(int(number) / (1000 * 1000 * 10000), 4)

def coin_name(denom):
    if denom == 'ubcre':
        return 'BCRE'
    if denom == 'ucre':
        return 'CRE'
    if denom == 'ibc/C4CFF46FD6DE35CA4CF4CE031E643C8FDC9BA4B99AE598E9B0ED98FE3A2319F9':
        return 'ATOM'
    if denom == 'ibc/6F4968A73F90CF7DE6394BF937D6DF7C7D162D74D839C13F53B41157D315E05F':
        return 'UST'
    return denom

def get_crescent_transaction(type_message, message):
    if type_message == '/crescent.liquidity.v1beta1.MsgLimitOrder':
        return f"SWAP {read_token(message['offer_coin']['amount'])} {coin_name(message['offer_coin']['denom'])} TO " \
               f"{read_token(message['amount'])} {coin_name(message['demand_coin_denom'])} " \
               f"(price {round(float(message['price']), 2)})"
    if type_message == '/crescent.liquidity.v1beta1.MsgWithdraw':
        return f"WITHDRAW {read_big_token(message['pool_coin']['amount'])} FROM POOL {message['pool_id']}"
    if type_message == '/crescent.farming.v1beta1.MsgStake':
        return f"STAKE {read_big_token(message['staking_coins'][0]['amount'])} TO {message['staking_coins'][0]['denom']}"
    if type_message == '/crescent.farming.v1beta1.MsgUnstake':
        return f"UNSTAKE {read_big_token(message['unstaking_coins'][0]['amount'])} FROM  {message['unstaking_coins'][0]['denom']}"
    if type_message == '/crescent.farming.v1beta1.MsgHarvest':
        return f"HARVEST {message['staking_coin_denoms'][0]}"
    if type_message == '/crescent.liquidity.v1beta1.MsgDeposit':
        depot0 = message['deposit_coins'][0]
        depot1 = message['deposit_coins'][1]
        return f"DEPOSIT {read_token(depot0['amount'])} {coin_name(depot0['denom'])} AND {read_token(depot1['amount'])}" \
               f" {coin_name(depot1['denom'])} TO POOL {message['pool_id']}"

    print(type_message)
    print(message)
    return 'CRESCENT'