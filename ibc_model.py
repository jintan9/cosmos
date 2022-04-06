import datetime
import requests
from constants.list_validators import list_validators
ONE_MILLION = 1000 * 1000
ONE_BILLION = 1000 * 1000 * 1000

COSMO_API = ['ROWAN', 'STAR']

def get_time(time_str):
    return datetime.datetime.strptime(time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')

class IBCToken:

    def __init__(self, token, coingecko_id, unbounding_time, api_keplr, api_cosmostation, lcd_cosmostation,
                 division=ONE_MILLION):
        self.address = None
        self.api_keplr = api_keplr
        self.lcd_cosmostation = lcd_cosmostation
        self.api_cosmostation = api_cosmostation
        self.token = token
        self.coingecko_id = coingecko_id
        self.unbounding_time = unbounding_time
        self.prices_by_token = None
        self.total_value = 0
        self.division = division

    def get_total_value(self, verbose=False):
        if verbose:
            print(f"TOTAL FOR {self.token} CHAIN : {round(self.total_value, 2)} UST")
        return round(self.total_value, 2)

    @staticmethod
    def get_price_by_token(list_entries=None):
        list_price = requests.get('https://api-osmosis.imperator.co/tokens/v2/all').json()
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
                info_token = double_entries[price_token['symbol']]
                if type(info_token) == str:
                    #list_entries as str
                    new_symbol = double_entries[price_token['symbol']]
                    division = ONE_MILLION
                else:
                    #list_entries as dict
                    new_symbol = double_entries[price_token['symbol']]['symbol']
                    division = double_entries[price_token['symbol']]['division']

                all_prices[new_symbol] = dict(name=price_token['symbol'],
                                              division=division,
                                              price=price_token['price'])


        all_prices['ibc/9989AD6CCA39D1131523DB0617B50F6442081162294B4795E26746292467B525']['division'] = ONE_MILLION * 1000 # LIKE
        all_prices['ibc/7A08C6F11EF0F59EB841B9F788A87EC9F2361C7D9703157EC13D940DC53031FA']['division'] = ONE_MILLION * 1000 # CHEQ
        all_prices['ibc/8061A06D3BD4D52C4A28FFECF7150D370393AF0BA661C3776C54FF32836C3961']['division'] = ONE_BILLION * ONE_BILLION # PSTAKE
        all_prices['ibc/8318FD63C42203D16DDCAF49FE10E8590669B3219A3E87676AC9DA50722687FB']['division'] = ONE_BILLION * ONE_BILLION # ROWAN

        return all_prices

    def set_price_by_token(self, list_entries=None):
        self.prices_by_token = self.get_price_by_token(list_entries)

    def get_balance(self):
        list_tokens = requests.get(self.get_balance_url()).json()
        if 'result' in list_tokens:
            list_tokens = list_tokens['result']
        else:
            list_tokens = list_tokens['balances']
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
        self.total_value += total_money

    def url_last_txs(self, limit, offset):
        return f'{self.api_cosmostation}v1/account/new_txs/{self.address}?limit={limit}&from={offset}'

    @property
    def url_list_validators(self):
        return f'{self.api_cosmostation}v1/staking/validators'

    def last_transactions(self, limit=50, offset=0):
        return requests.get(self.url_last_txs(limit, offset)).json()

    def list_validators(self):
        all_validators = requests.get(self.url_list_validators).json()
        ranks_validators = dict()
        for val in all_validators:
            ranks_validators[val['operator_address']] = dict(rank=val['rank'],
                                                             moniker=val['moniker'])
        return ranks_validators

    def get_delegation_url(self):
        if self.token in COSMO_API:
            return self.lcd_cosmostation + 'cosmos/staking/v1beta1/delegations/' + self.address
        return self.api_keplr + 'staking/delegators/' + self.address + '/delegations'

    def get_unbouding_url(self):
        if self.token in COSMO_API:
            return self.lcd_cosmostation + 'cosmos/staking/v1beta1/delegators/' + self.address + '/unbonding_delegations'
        return self.api_keplr + 'staking/delegators/' + self.address + '/unbonding_delegations'

    def get_balance_url(self):
        if self.token in COSMO_API:
            return self.lcd_cosmostation + 'cosmos/bank/v1beta1/balances/' + self.address
        return self.api_keplr + 'bank/balances/' + self.address

    def get_percent_delegation(self, recalculate_ranks=False, verbose=False):
        if recalculate_ranks:
            ranks_validators = self.list_validators()
            if verbose:
                print(ranks_validators)
        else:
            ranks_validators = list_validators[self.token]

        validators = requests.get(self.get_delegation_url()).json()
        if 'result' in validators:
            my_delegation = validators['result']
        else:
            my_delegation = validators['delegation_responses']
        total = sum([int(x['balance']['amount']) for x in my_delegation]) / self.division

        price_token = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={self.coingecko_id}&vs_currencies=usd').json()
        total_money = round(total * price_token[self.coingecko_id]['usd'], 2)
        self.total_value += total_money

        print(f'TOTAL STAKING {total} {self.token} / {self.total_value} UST')
        for delegation in my_delegation:
            info_validator = ranks_validators[delegation['delegation']['validator_address']]
            montant = int(delegation['balance']['amount']) / self.division
            if montant > 0:
                print(f"{info_validator} :  {montant} {self.token} soit {round(montant * 100 / total, 2)} %")

    def get_info_validator(self, current_address):
        return list_validators[self.token][current_address]['moniker']

    def get_unbounding_info(self):
        infos = requests.get(self.get_unbouding_url()).json()
        if 'result' in infos:
            infos = infos['result']
        else:
            infos = infos['unbonding_responses']
        if len(infos) == 0:
            return
        print('UNBOUNDING')
        for unbound in infos:
            moniker_src = self.get_info_validator(unbound['validator_address'])
            end_time = get_time(unbound['entries'][0]['completion_time'])
            balance = int(unbound['entries'][0]['balance']) / self.division
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
        print(self.api_keplr)
        list_proposals = requests.get(self.api_keplr + 'gov/proposals?limit=1000').json()['result']

        for prop in list_proposals:
            nb_proposals += 1
            end_time = datetime.datetime.strptime(prop['voting_end_time'][:19], '%Y-%m-%dT%H:%M:%S')
            if end_time > now + datetime.timedelta(hours=5):
                try:
                    title = prop['content']['title']
                except KeyError:
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
        url = self.api_keplr + 'gov/proposals/' + prop['id'] + '/votes/' + self.address
        has_voted = requests.get(url).json()
        print(has_voted)
        if 'error' in has_voted:
            print('==> HAS NOT VOTED')
            return False
        print('==> HAS VOTED')
        return True


class ATOM(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-cosmoshub.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-cosmos.cosmostation.io/',
                         api_cosmostation='https://api.cosmostation.io/',
                         coingecko_id='cosmos',
                         token='ATOM')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['ATOM'] = 'uatom'
        list_entries['OSMO'] = 'ibc/14F9BC3E44B8A9C1BE1FB08980FAB87034C9905EF17CF2F5008FC085218811CC'
        list_entries['LIKE'] = dict(symbol='ibc/1D5826F7EDE6E3B13009FEF994DC9CAAF15CC24CA7A9FF436FFB2E56FD72F54F',
                                    division=ONE_MILLION * 1000)
        list_entries['CRO'] = 'ibc/C932ADFE2B4216397A4F17458B6E4468499B86C3BC8116180F85D799D6F5CC1B'
        self.set_price_by_token(list_entries)

class Osmo(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-osmosis.keplr.app/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-osmosis.cosmostation.io/',
                         api_cosmostation='https://api-osmosis.cosmostation.io/',
                         coingecko_id='osmosis',
                         token='OSMO')
        self.address = address
        self.all_pools = None
        self.pools_total_share = {}

    def get_pool_liquidity(self, id_pool):
        if self.all_pools is None:
            self.all_pools = requests.get('https://api-osmosis.imperator.co/search/v1/pools').json()

        name = f"{self.all_pools[id_pool][0]['symbol']}/{self.all_pools[id_pool][1]['symbol']}"
        return name, self.all_pools[id_pool][0]['liquidity']

    def get_pool_total_shares(self, id_pool):
        if id_pool not in self.pools_total_share:
            infos = requests.get(self.api_keplr + 'osmosis/gamm/v1beta1/pools/' + id_pool).json()
            self.pools_total_share[id_pool] = int(infos['pool']['totalShares']['amount'])
        return self.pools_total_share[id_pool]

    def liquidity_by_pool(self, lp):
        id_pool = lp['denom'].split('/')[-1]
        my_shares = int(lp['amount'])
        total_shares = self.get_pool_total_shares(id_pool)
        name, liquidity = self.get_pool_liquidity(id_pool)
        return name, round(my_shares / total_shares * liquidity, 2)

    def get_pools(self):
        print('POOLS')
        total_money = 0

        list_lp = requests.get(self.api_keplr + 'osmosis/lockup/v1beta1/account_locked_coins/' + self.address).json()['coins']
        for lp in sorted(list_lp, key=lambda x: x['denom']):

            nb_lp = round(int(lp['amount']) / (ONE_BILLION * ONE_BILLION), 4)
            try:
                name, ust = self.liquidity_by_pool(lp)
                total_money += ust
                print(f"{lp['denom']} ({name}) {nb_lp} LP // {ust} UST")
            except KeyError:
                print(lp['denom'], nb_lp)
        print(f"TOTAL IN POOLS : {total_money} UST")
        self.total_value += total_money

    def get_info_precise(self, lp, lock):
        nb_lp = round(int(lp['amount']) / (ONE_BILLION * ONE_BILLION), 4)

        try:
            name, ust = self.liquidity_by_pool(lp)
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
                                                                    name,
                                                                    nb_lp, ust, duration)
        return '%s (%s) %s LP // %s UST // LOCK DURATION %s // END TIME %s' % (
            lp['denom'], name, nb_lp, ust, duration, lock['end_time'])

    def get_precise_pools(self):
        print('MORE PRECISE')
        list_locks = requests.get(self.api_keplr + 'osmosis/lockup/v1beta1/account_locked_longer_duration/' + self.address).json()['locks']
        for lock in sorted(list_locks, key=lambda x: x['coins'][0]['denom']):
            current_lp = lock['coins'][0]
            print(self.get_info_precise(current_lp, lock))


class Secret(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-secret.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-secret.cosmostation.io/',
                         api_cosmostation='https://api-secret.cosmostation.io/',
                         coingecko_id='secret',
                         token='SCRT',)
        self.address = address


class Akash(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-akash.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-akash.cosmostation.io/',
                         api_cosmostation='https://api-akash.cosmostation.io/',
                         coingecko_id='akash-network',
                         token='AKT',)
        self.address = address


class Chihuahua(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://api.chihuahua.wtf/',
                         unbounding_time=28,
                         lcd_cosmostation='https://lcd-chihuahua.cosmostation.io/',
                         api_cosmostation='https://api-chihuahua.cosmostation.io/',
                         coingecko_id='chihuahua-token',
                         token='CHIHUAHUA')
        self.address = address


class Stargaze(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-stargaze.keplr.app/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-stargaze.cosmostation.io/',
                         api_cosmostation='https://api-stargaze.cosmostation.io/',
                         coingecko_id='stargaze',
                         token='STAR')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['STARS'] = 'ustars'
        self.set_price_by_token(list_entries)


class Juno(IBCToken):

    def __init__(self, address):
        super().__init__('JUNO',
                         coingecko_id='juno-network',
                         api_keplr='https://lcd-juno.keplr.app/',
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


class Sifchain(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://lcd-sifchain.keplr.app/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-sifchain.cosmostation.io/',
                         api_cosmostation='https://api-sifchain.cosmostation.io/',
                         coingecko_id='sifchain',
                         division=ONE_BILLION * ONE_BILLION,
                         token='ROWAN')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['ROWAN'] =  dict(symbol='rowan',
                                      division=ONE_BILLION * ONE_BILLION)
        self.set_price_by_token(list_entries)


class Crescent(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://api-kava.cosmostation.io/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-crescent.cosmostation.io/',
                         api_cosmostation='https://api-crescent.cosmostation.io/',
                         coingecko_id='crescent',
                         token='CRE')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['ROWAN'] =  dict(symbol='rowan',
                                      division=ONE_BILLION * ONE_BILLION)
        self.set_price_by_token(list_entries)

class Kava(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://api-kava.cosmostation.io/',
                         unbounding_time=21,
                         lcd_cosmostation='https://lcd-kava.cosmostation.io/',
                         api_cosmostation='https://api-kava.cosmostation.io/',
                         coingecko_id='kava',
                         token='KAVA')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['ROWAN'] =  dict(symbol='rowan',
                                      division=ONE_BILLION * ONE_BILLION)
        self.set_price_by_token(list_entries)