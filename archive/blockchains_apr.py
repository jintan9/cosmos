import requests

list_price = requests.get('https://api-osmosis.imperator.co/tokens/v1/all').json()
price_infos = dict()
for price_token in list_price:
    price_infos[price_token['name']] = price_token['price']


infos = dict()

infos = dict()
infos['Chihuahua'] = dict(number_token=13650, apr=398)
infos['Juno'] = dict(number_token=25.3, apr=120)
infos['Osmosis'] = dict(number_token=52, apr=88)
infos['Stargaze'] = dict(number_token=500, apr=110)
infos['Desmos'] = dict(number_token=42, apr=65)

results = dict()
for token in infos:
    price = price_infos[token]
    money_value = round(price * infos[token]['number_token'], 2)
    apr_day = infos[token]['apr'] / (100 * 365)
    token_earned = round(infos[token]['number_token'] * apr_day, 2)
    money_earned = round(token_earned * price, 2)
    print(token, ':', token_earned, token, 'soit', money_earned, 'USD', 'investi', money_value, 'USD')
    results[token] = money_earned

print('')
for token in sorted(results.items(), key=lambda x: x[1], reverse=True):
    print(token)

