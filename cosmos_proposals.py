import requests
import datetime
from cosmos_addresses import list_tokens

def has_voted_proposals(ibc_obj, prop):
    url = ibc_obj.api + 'gov/proposals/' + prop['id'] + '/votes/' + ibc_obj.address
    has_voted = requests.get(url).json()
    print(has_voted)
    if 'error' in has_voted:
        print('==> HAS NOT VOTED')
        return False
    print('==> HAS VOTED')
    return True

def show_ongoing_proposals(ibc_obj):
    token = ibc_obj.token
    print(f'==== {token} ====')
    now = datetime.datetime.now()
    nb_proposals = 0
    nb_ongoing_proposals = 0
    nb_voted = 0
    list_not_voted = []
    list_proposals = requests.get(ibc_obj.api + 'gov/proposals?limit=1000').json()['result']

    for prop in list_proposals:
        nb_proposals += 1
        end_time = datetime.datetime.strptime(prop['voting_end_time'][:19], '%Y-%m-%dT%H:%M:%S')
        if end_time > now:
            title = prop['content']['value']['title']
            print(title, 'START', prop['voting_start_time'], 'END', prop['voting_end_time'])
            nb_ongoing_proposals += 1
            if has_voted_proposals(ibc_obj, prop):
                nb_voted += 1
            else:
                list_not_voted.append([dict(adress=ibc_obj.address, title=title)])

    if nb_ongoing_proposals >= 1:
        print(f'FOR {token} : {nb_voted} voted proposals out of {nb_ongoing_proposals}')

    print(f'FOR {token} : {nb_ongoing_proposals} ongoing proposals out of {nb_proposals}')
    print('')
    return dict(nb_voted=nb_voted, nb_ongoing_proposals=nb_ongoing_proposals,
                list_not_voted=list_not_voted)


total = dict(nb_voted=0, nb_ongoing_proposals=0)
all_not_voted = []
for token_infos in list_tokens:
    infos = show_ongoing_proposals(token_infos)

    for key in total:
        total[key] += infos[key]
    all_not_voted.extend(infos['list_not_voted'])

print('TOTAL')
print(f"{total['nb_voted']} voted out of {total['nb_ongoing_proposals']} ongoing")
for not_voted in all_not_voted:
    print(not_voted)


