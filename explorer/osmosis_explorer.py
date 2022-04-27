
def get_osmosis_transaction(type_message, message):
    print(type_message)
    print(message)
    if type_message == '/osmosis.gamm.v1beta1.MsgJoinPool':
        return f"JOIN LP {message['poolId']}"
    if type_message == '/osmosis.lockup.MsgLockTokens':
        return f"LOCK LP {message['coins'][0]['denom']} FOR {int(message['duration'][:-1]) / 86400} DAYS"

    if type_message == '/osmosis.lockup.MsgBeginUnlocking':
        return 'Unlocking LP'
    if type_message == '/osmosis.superfluid.MsgSuperfluidDelegate':
        return 'Superfluid Staking'
    return 'OSMOSIS'