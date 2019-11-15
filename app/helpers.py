import json
import re
from datetime import datetime, timedelta
import bs4
import requests
from app.__init__ import Cache, db


def run(type_int):
    # Check type (int in DB) to build url endpoint
    type_to_fetch = None
    if type_int == 1:
        type_to_fetch = "livres"
    elif type_int == 2:
        type_to_fetch = "films"
    elif type_int == 3:
        type_to_fetch = "series"
    elif type_int == 4:
        type_to_fetch = "jeuxvideo"

    # DB query (cache table)
    queryTest = Cache.query.filter_by(type=type_int).first()

    if queryTest is not None and queryTest.data is not None:
        since = datetime.now() - timedelta(hours=96)

        # Check if cache is younger than 24 hours. If yes, take cache. If not, scrape page (fetchDatas method)
        if queryTest.created_at > since:
            print('from DB')
            return queryTest.data
        else:
            print('from scrap')
            itemsList = fetchDatas(type_to_fetch)
            # Update data in DB
            db.session.query(Cache).filter_by(type=type_int).update({'data': json.dumps(itemsList)})
            db.session.commit()
            return json.dumps(itemsList)
    else:
        print('from DB 1st insert')
        # API call from helpers.py
        itemsList = fetchDatas(type_to_fetch)
        # DB insert
        cache = Cache(data=json.dumps(itemsList), type=type_int)
        db.session.add(cache)
        db.session.commit()
        return json.dumps(itemsList)


def fetchDatas(type_string):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
    if type_string == "films":
        url = "https://www.senscritique.com/" + type_string + "/toujours-a-l-affiche"
    else:
        url = "https://www.senscritique.com/" + type_string + "/actualite"
    res = requests.get(url, headers=headers)

    try:
        res.raise_for_status()
    except Exception as exc:
        print("This is a problem:" + str(exc))

    # Parse html page
    soup = bs4.BeautifulSoup(res.text, features='html.parser')
    items = soup.select(".elpr-content")

    # Get images
    images = soup.find_all("img", itemprop="image")
    srcs = []
    for src in images:
        srcs.append(src["src"])

    # Construct list of dictionnaries, each dict represent an item
    itemsList = []
    titleTag = ''
    if type_string == 'films':
        titleTag = 'h2'
    else:
        titleTag = 'h3'
    for idx, elem in enumerate(items):
        item = {}
        item['image'] = srcs[idx]
        item['title'] = re.sub('[\n|\t]', '', elem.find(titleTag).text.strip())
        baseline = elem.find_all('p', {'class': 'elco-baseline'})
        item['sortie'] = re.sub('[\n|\t]', '', baseline[0].text.strip())
        item['author'] = re.sub('Livre|\t|\n|de', '',
                                baseline[1].text).strip()

        description = elem.find('p', {'class': 'elco-description'})
        if description is not None:
            item['description'] = description.text
        else:
            item['description'] = ''

        itemsList.append(item)
    return itemsList
