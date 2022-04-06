from constants.cosmos_addresses import all_addresses

total = dict(nb_voted=0, nb_ongoing_proposals=0)
all_not_voted = []
for ibc_obj in all_addresses:
    try:
        infos = ibc_obj.show_ongoing_proposals()

        for key in total:
            total[key] += infos[key]
        all_not_voted.extend(infos['list_not_voted'])
    except Exception as e:
        print('EXCEPTION', e)

print('TOTAL')
print(f"{total['nb_voted']} voted out of {total['nb_ongoing_proposals']} ongoing")
for not_voted in all_not_voted:
    print(not_voted)


