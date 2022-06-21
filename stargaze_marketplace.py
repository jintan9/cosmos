import requests

address = 'https://api.mintscan.io/v1/stargaze/wasm/contracts/stars1fvhcnyddukcqfnt7nlwv3thm5we22lyxyxylr9h77cvgkcn43xfsvgv0pl/txs?limit=45&offset=0'
print(requests.get(address).json())

for tx in requests.get(address).json():
    print(tx)
