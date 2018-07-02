import json
import urllib.request
from twitter import Twitter, OAuth, TwitterHTTPError, TwitterStream 
from bs4 import BeautifulSoup
import requests
from pytrends.request import TrendReq
import datetime
from pushbullet.pushbullet import PushBullet
from tokens import A_S, A_T, C_K, C_S, API_KEY

now = datetime.datetime.now()

#twitter
ACCESS_TOKEN = A_T
ACCESS_SECRET = A_S
CONSUMER_KEY = C_K
CONSUMER_SECRET = C_S

oauth = OAuth(ACCESS_TOKEN, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
twitter = Twitter(auth=oauth)

#run the script twice a day
if now.hour in [15,18]:
    #polish
    pol_trends = twitter.trends.place(_id = 23424923)
    twittrendlistPL=[]
    for i in pol_trends[0]['trends']:
        twittrendlistPL.append(i['name'])
    strPLT=" ,".join(str(x) for x in twittrendlistPL[0:15])
    #print(strPLT)


    #global trends
    globaltrends=twitter.trends.place(_id = 1)
    twittrendlist=[]
    for i in globaltrends[0]['trends']:
        twittrendlist.append(i['name'])    
    def isEnglish(s):
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True    
    G=[i for i in twittrendlist if isEnglish(i)]
    strGT=" ,".join(str(x) for x in G[0:15])
    #print(strGT)


    #Google Trends

    pytrends = TrendReq(geo='GB-ENG',tz=360)
    df=pytrends.trending_searches()
    gtrendsus=df.title.tolist()
    strGog=" ,".join(str(x) for x in gtrendsus[0:15])
    #print(strGog)

    #yahoo trending charts


    page = requests.get("https://finance.yahoo.com/trending-tickers/")
    soup = BeautifulSoup(page.content, 'html.parser')
    base=soup.findAll('td', {'class':'data-col1 Ta(start) Pstart(10px) Miw(180px)'})
    yhoo=[]
    for i in base:
        yhoo.append(i.get_text())
    strYHOO=" ,".join(str(x) for x in yhoo[0:15])


    #crypto trends to find

    with urllib.request.urlopen("https://api.coinmarketcap.com/v2/ticker/") as url:
        cmc = json.loads(url.read().decode())
    names=[]
    change=[]
    for i in cmc['data']:
        names.append(cmc['data'][i]['symbol'])
        change.append(cmc['data'][i]['quotes']['USD']['percent_change_24h'])
    change, names = zip(*sorted(zip(change, names)))
    cmcstr=' ,'.join([str(a) + ': '+ str(b) + '%' for a,b in zip(names[-5:],change[-5:])])

    apiKey = API_KEY
    p = PushBullet(apiKey)
    # Get a list of devices
    devices = p.getDevices()
    devices

    p.pushNote(devices[0]["iden"], 'Daily news ', "***TREND TWT POLSKA:" + strPLT + "\n***TREND TWT GLOBAL: " + strGT + "\n***G US SEARCH: " + strGog + "\n***TOP TICKERS YAHOO: " + strYHOO + "\n***CMC TOP: " + cmcstr)
    print('yes')
else:
    print('not')
