
ONE_MILLION = 1000 * 1000
ONE_BILLION = 1000 * 1000 * 1000

def read_token(number):
    return round(int(number) / ONE_MILLION, 4)

def read_big_token(number):
    return round(int(number) / (ONE_MILLION * 10000), 4)

def read_token_rowan(number):
    return round(int(number) / (ONE_BILLION * ONE_BILLION), 4)
