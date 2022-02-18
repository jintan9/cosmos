import requests
nomic_apr = requests.get('https://app.nomic.io:8443/minting/inflation').json()['result']

class Compounder:

    def __init__(self, token, apr, fees, number_actions=2):
        self.token = token
        self.apr = apr
        self.fees = fees * number_actions

nomic = Compounder('NOM', apr=round(float(nomic_apr) * 100, 2), fees=0.01)
desmos = Compounder('DSM', apr=84, fees=0.002)
atom = Compounder('ATOM', apr=15, fees=0.0025, number_actions=1)
juno = Compounder('JUNO', apr=120, fees=0.0016, number_actions=1)


class Compound:
    def __init__(self, initial_noms, compound_hours, token_data):
        self.NUMBER_HOURS_PER_MONTH = 24 * 30
        self.initial_noms = initial_noms
        self.compound_hours = compound_hours
        self.token_data = token_data

    def get_apr(self):
        return self.token_data.apr

    def apr_per_hour(self):
        return self.token_data.apr / 365 / 24 / 100

    def first_reward(self):
        return self.initial_noms * self.apr_per_hour() * self.compound_hours

    def calculate_interest(self, verbose=False):
        number_hours = 0
        number_noms = self.initial_noms
        while number_hours < (self.NUMBER_HOURS_PER_MONTH - self.compound_hours):
            rewards = number_noms * self.apr_per_hour() * self.compound_hours
            number_noms = number_noms + rewards - self.token_data.fees
            number_hours += self.compound_hours

        # Last reward
        rewards = number_noms * self.apr_per_hour() * (self.NUMBER_HOURS_PER_MONTH - number_hours)
        number_noms = number_noms + rewards - self.token_data.fees
        if verbose:
            print(f'If compound every {self.compound_hours} hours, total is {number_noms}')
        return dict(number_noms=number_noms, first_reward=self.first_reward())


def find_best_apr(number_of_token, token_data):
    infos = dict()
    print('')
    for x in range(1, 24*7):
        infos[x] = Compound(number_of_token, x, token_data).calculate_interest()

    print(f"====For {number_of_token} {token_data.token} ====")
    for x in sorted(infos.items(), key=lambda x: x[1]['number_noms'], reverse=True)[:5]:
        print(f"If compound every {x[0]} hours, total is {x[1]['number_noms']} "
              f"/ first_reward is {x[1]['first_reward']}")

    print('EVERY DAY')
    Compound(number_of_token, 24, token_data).calculate_interest(verbose=True)
    print('EVERY WEEK')
    Compound(number_of_token, 24*7, token_data).calculate_interest(verbose=True)

print('APR NOMIC', Compound(0,0, nomic).get_apr(), '%')
find_best_apr(3.94, nomic)
find_best_apr(7.35, nomic)
find_best_apr(44, desmos)
find_best_apr(26.25, atom)
find_best_apr(31, juno)
