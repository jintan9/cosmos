from ibc_common_model import IBCToken, ONE_MILLION, ONE_BILLION
import requests

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

    def get_precise_infos(self):
        self.get_price_by_token_custom()
        self.get_balance()


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

    def get_precise_infos(self):
        print('OSMO MORE PRECISE INFO')
        self.set_price_by_token()
        self.get_balance()
        self.get_pools()
        self.get_precise_pools()

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

    def get_precise_infos(self):
        self.get_price_by_token_custom()
        self.get_balance()


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

    def get_precise_infos(self):
        self.get_price_by_token_custom()
        self.get_balance()
        self.get_junoswap_balance()

    def get_junoswap_balance(self):
        print('===JUNOSWAP===')
        self.get_zeroxtracker_data('JunoSwap')

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

    def get_precise_infos(self):
        print('ROWAN MORE PRECISE INFO')
        self.get_price_by_token_custom()
        self.get_balance()
        self.get_sifchain_balance()

    def get_sifchain_balance(self):
        print('=== LP SIFCHAIN ===')
        self.get_zeroxtracker_data('Sifchain')

class Crescent(IBCToken):

    def __init__(self, address):
        super().__init__(api_keplr='https://api-crescent.cosmostation.io/',
                         unbounding_time=14,
                         lcd_cosmostation='https://lcd-crescent.cosmostation.io/',
                         api_cosmostation='https://api-crescent.cosmostation.io/',
                         coingecko_id='crescent',
                         token='CRE')
        self.address = address

    def get_price_by_token_custom(self):
        list_entries = dict()
        list_entries['BCRE'] = 'ubre'
        list_entries['ATOM'] = 'ibc/C4CFF46FD6DE35CA4CF4CE031E643C8FDC9BA4B99AE598E9B0ED98FE3A2319F9'
        list_entries['UST'] = 'ibc/6F4968A73F90CF7DE6394BF937D6DF7C7D162D74D839C13F53B41157D315E05F'

        self.set_price_by_token(list_entries)

    def get_precise_infos(self):
        print('CRESCENT MORE PRECISE INFO')
        self.get_price_by_token_custom()
        self.get_balance()
        self.get_crescent_balance()

    def get_crescent_balance(self):
        print('====LP CRESCENT===')
        self.get_zeroxtracker_data('Crescent')

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