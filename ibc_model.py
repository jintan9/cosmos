import datetime
import requests
from constants.list_validators import list_validators
ONE_MILLION = 1000 * 1000
ONE_BILLION = 1000 * 1000 * 1000

def get_time(time_str):
    return datetime.datetime.strptime(time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')

class IBCToken:

    def __init__(self, token, unbounding_time, api, api_cosmostation, lcd_cosmostation):
        self.address = None
        self.api = api
        self.lcd_cosmostation = lcd_cosmostation
        self.api_cosmostation = api_cosmostation
        self.token = token
        self.unbounding_time = unbounding_time
        self.prices_by_token = None

    @staticmethod
    def get_price_by_token(list_entries=None):
        list_price = requests.get('https://api-osmosis.imperator.co/tokens/v1/all').json()

        all_prices = dict()

        if list_entries is None:
            double_entries = dict()
        else:
            double_entries = list_entries

        for price_token in list_price:
            all_prices[price_token['denom']] = dict(name=price_token['symbol'],
                                                    division=ONE_MILLION,
                                                    price=price_token['price'])
            if price_token['symbol'] in double_entries:
                new_symbol = double_entries[price_token['symbol']]
                all_prices[new_symbol] = dict(name=price_token['symbol'],
                                              division=ONE_MILLION,
                                              price=price_token['price'])
        all_prices['ibc/8318FD63C42203D16DDCAF49FE10E8590669B3219A3E87676AC9DA50722687FB']['division'] = ONE_MILLION * ONE_MILLION * ONE_MILLION

        return all_prices

    def set_price_by_token(self, list_entries=None):
        self.prices_by_token = self.get_price_by_token(list_entries)

    def get_balance(self):
        list_tokens = requests.get(self.api + 'bank/balances/' + self.address).json()['result']
        total_money = 0
        print('===BALANCE===')
        for coin in list_tokens:
            try:
                info_coin = self.prices_by_token[coin['denom']]
                nb_coin = round(int(coin['amount']) / info_coin['division'], 4)
                ust = round(nb_coin * info_coin['price'], 2)
                total_money += ust
                print(f"{info_coin['name']} : {nb_coin} // {ust} UST")
            except KeyError:
                print(coin)
        print(f"TOTAL IN BALANCE : {total_money} UST")

    @property
    def last_txs(self):
        return self.api_cosmostation + 'v1/account/new_txs/' + self.address + '?limit=5&from=0'

    @property
    def url_list_validators(self):
        return self.api_cosmostation + 'v1/staking/validators'

    def list_validators(self):
        all_validators = requests.get(self.url_list_validators).json()
        ranks_validators = dict()
        for val in all_validators:
            ranks_validators[val['operator_address']] = dict(rank=val['rank'],
                                                             moniker=val['moniker'])
        return ranks_validators

    def get_percent_delegation(self, recalculate_ranks=False):
        if recalculate_ranks:
            ranks_validators = self.list_validators()
        else:
            ranks_validators = list_validators[self.token]

        validators = requests.get(self.api + 'staking/delegators/' + self.address + '/delegations').json()
        my_delegation = validators['result']
        total = sum([int(x['balance']['amount']) for x in my_delegation]) / ONE_MILLION
        print(f'TOTAL STAKING {total} {self.token}')
        for delegation in my_delegation:
            info_validator = ranks_validators[delegation['delegation']['validator_address']]
            montant = int(delegation['balance']['amount']) / ONE_MILLION
            if montant > 0:
                print(f"{info_validator} :  {montant} {self.token} soit {round(montant * 100 / total, 2)} %")

    def get_info_validator(self, current_address):
        return list_validators[self.token][current_address]['moniker']

    def get_unbounding_info(self):
        infos = requests.get(self.api + 'staking/delegators/' + self.address + '/unbonding_delegations').json()['result']
        if len(infos) == 0:
            return
        print('UNBOUNDING')
        for unbound in infos:
            moniker_src = self.get_info_validator(unbound['validator_address'])
            end_time = get_time(unbound['entries'][0]['completion_time'])
            balance = int(unbound['entries'][0]['balance']) / ONE_MILLION
            start_time = end_time - datetime.timedelta(days=self.unbounding_time)
            print(f"UNBOUND {balance} {self.token} FROM {moniker_src} | started : {start_time} | end : {end_time}")

    def get_redelegation_info(self):
        infos = requests.get(self.lcd_cosmostation + 'cosmos/staking/v1beta1/delegators/' + self.address +
                             '/redelegations').json()['redelegation_responses']

        if len(infos) == 0:
            return
        print('REDELEGATION')
        for redelegation in infos:
            redel = redelegation['redelegation']
            moniker_src = self.get_info_validator(redel['validator_src_address'])
            moniker_dst = self.get_info_validator(redel['validator_dst_address'])
            end_time = get_time(redelegation['entries'][0]['redelegation_entry']['completion_time'])
            start_time = end_time - datetime.timedelta(days=self.unbounding_time)
            print(f"FROM {moniker_src} TO {moniker_dst} | started : {start_time} | end : {end_time}")

    def show_ongoing_proposals(self):
        print(f'==== {self.token} ====')
        now = datetime.datetime.now()
        nb_proposals = 0
        nb_ongoing_proposals = 0
        nb_voted = 0
        list_not_voted = []
        list_proposals = requests.get(self.api + 'gov/proposals?limit=1000').json()['result']

        for prop in list_proposals:
            nb_proposals += 1
            end_time = datetime.datetime.strptime(prop['voting_end_time'][:19], '%Y-%m-%dT%H:%M:%S')
            if end_time > now + datetime.timedelta(hours=5):
                title = prop['content']['value']['title']
                print(f"{title} START {prop['voting_start_time']} END {prop['voting_end_time']}")
                nb_ongoing_proposals += 1
                if self.has_voted_proposals(prop):
                    nb_voted += 1
                else:
                    list_not_voted.append([dict(adress=self.address, title=title)])

        if nb_ongoing_proposals >= 1:
            print(f'FOR {self.token} : {nb_voted} voted proposals out of {nb_ongoing_proposals}')

        print(f'FOR {self.token} : {nb_ongoing_proposals} ongoing proposals out of {nb_proposals}')
        print('')
        return dict(nb_voted=nb_voted, nb_ongoing_proposals=nb_ongoing_proposals,
                    list_not_voted=list_not_voted)
    def has_voted_proposals(self, prop):
        url = self.api + 'gov/proposals/' + prop['id'] + '/votes/' + self.address
        has_voted = requests.get(url).json()
        print(has_voted)
        if 'error' in has_voted:
            print('==> HAS NOT VOTED')
            return False
        print('==> HAS VOTED')
        return True


class ATOM(IBCToken):

    def __init__(self, address):
        super().__init__(api='https://lcd-cosmoshub.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-cosmos.cosmostation.io/',
                         api_cosmostation='https://api.cosmostation.io/',
                         token='ATOM')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['ATOM'] = 'uatom'
        list_entries['OSMO'] = 'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC'
        list_entries['LIKE'] = 'ibc/1D5826F7EDE6E3B13009FEF994DC9CAAF15CC24CA7A9FF436FFB2E56FD72F54F'
        list_entries['CRO'] = 'ibc/C932ADFE2B4216397A4F17458B6E4468499B86C3BC8116180F85D799D6F5CC1B'
        self.set_price_by_token(list_entries)

class Osmo(IBCToken):

    def __init__(self, address):
        super().__init__(api='https://lcd-osmosis.keplr.app/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-osmosis.cosmostation.io/',
                         api_cosmostation='https://api-osmosis.cosmostation.io/',
                         token='OSMO')
        self.address = address

    def prices_by_pool(self, lp):
        prices_by_pool = dict()
        prices_by_pool['gamm/pool/1'] = dict(name='OSMO/ATOM', value=1753.6/1519.8)
        prices_by_pool['gamm/pool/498'] = dict(name='ATOM/JUNO', value=37.6) # K
        prices_by_pool['gamm/pool/560'] = dict(name='OSMO/UST', value=1917/29.43)
        prices_by_pool['gamm/pool/562'] = dict(name='LUNA/UST', value=530/77.2)
        prices_by_pool['gamm/pool/577'] = dict(name='XKI/OSMO', value=500/0.28)
        prices_by_pool['gamm/pool/578'] = dict(name='XKI/UST', value=288/0.19)
        prices_by_pool['gamm/pool/584'] = dict(name='SCRT/OSMO', value=400/3.39)
        prices_by_pool['gamm/pool/592'] = dict(name='BTSG/UST', value=55/0.64)
        prices_by_pool['gamm/pool/601'] = dict(name='OSMO/CDMX', value=110/0.36)
        prices_by_pool['gamm/pool/604'] = dict(name='OSMO/STAR', value=430/0.003)
        prices_by_pool['gamm/pool/605'] = dict(name='HUAHUA/OSMO', value=159/14828)
        prices_by_pool['gamm/pool/606'] = dict(name='ATOM/HUAHUA', value=51/4981.4)
        prices_by_pool['gamm/pool/611'] = dict(name='ATOM/STAR', value=545/55.2)
        prices_by_pool['gamm/pool/613'] = dict(name='VDL/OSMO', value=1063/59.58) # M
        prices_by_pool['gamm/pool/619'] = dict(name='DSM/OSMO', value=90/8.8)
        prices_by_pool['gamm/pool/627'] = dict(name='SOMM/OSMO', value=885/47.9) # M
        prices_by_pool['gamm/pool/629'] = dict(name='ROWAN/OSMO', value=141/0.012) # M
        prices_by_pool['gamm/pool/631'] = dict(name='NETA/OSMO', value=444/102)
        return prices_by_pool[lp['denom']]

    def get_pools(self):
        print('POOLS')
        total_money = 0
        list_lp = requests.get(self.api + 'osmosis/lockup/v1beta1/account_locked_coins/' + self.address).json()['coins']
        for lp in sorted(list_lp, key=lambda x: x['denom']):
            nb_lp = round(int(lp['amount']) / (ONE_BILLION * ONE_BILLION), 4)
            try:
                info_pool = self.prices_by_pool(lp)
                ust = round(nb_lp * info_pool['value'], 2)
                total_money += ust
                print(f"{lp['denom']} ({info_pool['name']}) {nb_lp} LP // {ust} UST")
            except KeyError:
                print(lp['denom'], nb_lp)
        print(f"TOTAL IN POOLS : {total_money} UST")

    def get_info_precise(self, lp, lock):
        nb_lp = round(int(lp['amount']) / (ONE_BILLION * ONE_BILLION), 4)

        try:
            info_pool = self.prices_by_pool(lp)
            price = round(nb_lp * info_pool['value'], 2)
        except KeyError:
            return lp

        if '86400' in lock['duration']:
            duration = '1 DAY'
        elif '604800' in lock['duration']:
            duration = '7 DAYS'
        else:
            duration = '14 DAYS'

        if lock['end_time'] == '0001-01-01T00:00:00Z':
            return '%s (%s) %s LP // %s UST // LOCK DURATION %s' % (lp['denom'],
                                                                    info_pool['name'],
                                                                    nb_lp, price, duration)
        return '%s (%s) %s LP // %s UST // LOCK DURATION %s // END TIME %s' % (
            lp['denom'], info_pool['name'], nb_lp, price, duration, lock['end_time'])

    def get_precise_pools(self):
        print('MORE PRECISE')
        list_locks = requests.get(self.api + 'osmosis/lockup/v1beta1/account_locked_longer_duration/' + self.address).json()['locks']
        for lock in sorted(list_locks, key=lambda x: x['coins'][0]['denom']):
            current_lp = lock['coins'][0]
            print(self.get_info_precise(current_lp, lock))


class Secret(IBCToken):

    def __init__(self, address):
        super().__init__(api='https://lcd-secret.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-secret.cosmostation.io/',
                         api_cosmostation='https://api-secret.cosmostation.io/',
                         token='SCRT',)
        self.address = address


class Chihuahua(IBCToken):

    def __init__(self, address):
        super().__init__(api='https://api.chihuahua.wtf/',
                         unbounding_time=28,
                         lcd_cosmostation='https://lcd-chihuahua.cosmostation.io/',
                         api_cosmostation='https://api-chihuahua.cosmostation.io/',
                         token='CHIHUAHUA')
        self.address = address


class Stargaze(IBCToken):

    def __init__(self, address):
        super().__init__(api='https://rest.stargaze.publicawesome.dev/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-stargaze.cosmostation.io/',
                         api_cosmostation='https://api-stargaze.cosmostation.io/',
                         token='STAR')
        self.address = address


class Juno(IBCToken):

    def __init__(self, address):
        super().__init__('JUNO',
                         api='https://lcd-juno.keplr.app/',
                         unbounding_time=28,
                         lcd_cosmostation='https://lcd-juno.cosmostation.io/',
                         api_cosmostation='https://api-juno.cosmostation.io/')
        self.address = address

    def get_price_by_token_custom(self,):
        list_entries = dict()
        list_entries['JUNO'] = 'ujuno'
        list_entries['ATOM'] = 'ibc/C4CFF46FD6DE35CA4CF4CE031E643C8FDC9BA4B99AE598E9B0ED98FE3A2319F9'
        list_entries['UST'] = 'ibc/2DA4136457810BCB9DAAB620CA67BC342B17C3C70151CA70490A170DF7C9CB27'
        list_entries['OSMO'] = 'ibc/ED07A3391A112B175915CD8FAF43A2DA8E4790EDE12566649D0C2F97716B8518'

        self.set_price_by_token(list_entries)