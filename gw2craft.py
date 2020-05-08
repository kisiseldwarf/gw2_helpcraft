from bs4 import BeautifulSoup
import urllib
import urllib.request
import json
import sys
import webbrowser
from gw2api import GuildWars2Client


def usage():
    print("gw2craft {tier} {job}")

if len(sys.argv) < 3:
    usage()
    quit()

gw2_client = GuildWars2Client()
tier = sys.argv[1]
job = sys.argv[2]


## FUNCTIONS ##

def retrieve(site, tier):
    original_list = site.find(id=tier).findAll('div')
    list_names = []
    for child in original_list:
        list_names.append(child.contents[4].text)

    list_qt = site.find(id=tier).findAll("span",{"class":"quantity"})
    return list_names,list_qt


def getItemID(itemName):
    itemName = urllib.parse.quote(itemName)
    myUrl = "http://www.gw2spidy.com/api/v0.9/json/item-search/"+itemName+"/1"
    json_file = urllib.request.urlopen(myUrl)

    class json_results(object):
        def __init__ (self,data):
            self.__dict__ = json.loads(data)

    json_res = json_file.read().decode('utf-8')
    json_res = json_results(json_res)
    return json_res.results[0]['data_id']

def isPrimaryMaterial(itemID):
    endpoint_url = "https://api.guildwars2.com/v2/recipes/search?output="+str(itemID)
    json_file = urllib.request.urlopen(endpoint_url)

    class json_results(object):
        def __init__(self,data):
            self.list = json.loads(data)

    json_res = json_file.read().decode('utf-8')
    json_res = json_results(json_res)
    return len(json_res.list) == 0

def getItemName(itemID):
    item = gw2_client.items.get(id=itemID)
    print(item)
    return item['name']

def convertPriceToGold(price):
    gold = price // 10000
    rest = price - (gold * 10000)
    silver = rest // 100
    rest = rest - (silver * 100)
    copper = rest
    return gold,silver,copper

def getPrice(itemID):
    json_res = gw2_client.commerceprices.get(ids=[itemID])
    return json_res[0]['buys']['unit_price']

## MAIN

print("Retrieving items names and quantity from gw2craft...")
gw2crafturl = 'https://gw2crafts.net/'+job+'.html'
mysite = urllib.request.urlopen(gw2crafturl)
soup_mysite = BeautifulSoup(mysite,features="lxml")
list_names, list_qt = retrieve(soup_mysite,tier)
list_qt = list(map(lambda x : x.text, list_qt))

print("Retrieving items from name...")

list_primary = []
list_craftable = []
list_qt_primary = []
list_qt_craftable = []

i = 0
for item_name in list_names:
    itemID = getItemID(item_name)
    item = gw2_client.items.get(id=itemID)
    if(isPrimaryMaterial(item['id'])):
        list_primary.append(item)
        list_qt_primary.append(list_qt[i])
    else:
        list_craftable.append(item)
        list_qt_craftable.append(list_qt[i])
    i = i + 1

print('Retrieving Primary Materiels price\'s needed...')
if(len(list_primary) == 0):
    print('No primary materials needed !')
else:
    print('---- Careful !! -----')
    print('You should buy these too, they won\'t appear in the buying list of gw2 efficiency')
    print('Those are primary materials, which mean they can\'t be crafted and they need to be gathered or bought')
    print('---------------------')
    total_price = 0
    for item in list_primary:
        qt_index = list_primary.index(item)
        qt = list_qt_primary[qt_index]
        price = int(getPrice(item['id'])) * int(qt)
        total_price = int(total_price) + int(price)
        gold, silver, copper = convertPriceToGold(int(price))
        print(str(qt)+" "+item['name']+" for "+str(gold)+" gold, "+str(silver)+" silver, "+str(copper)+" copper")
    total_gold, total_silver, total_copper = convertPriceToGold(int(total_price))
    print('')
    print('It adds '+str(total_gold)+' gold, '+str(total_silver)+' silver, '+str(total_copper)+' copper to the final price.')
    print('this should be added to the total price gw2efficiency gives you')
    print('---------------------------')


print("Retrieving gw2efficiency URL...")
request = ""
for i in range(len(list_craftable) -1):
    if(i != len(list_craftable)-1):
        request = request + str(list_qt_craftable[i])+"-"+str(list_craftable[i]['id'])+";"
    if(i == len(list_craftable)-1):
        request = request + str(list_qt_craftable[i])+"-"+str(list_craftable[i]['id'])

gw2efficiencyurl = "https://gw2efficiency.com/crafting/calculator/a~0!b~1!c~0!d~"+request

webbrowser.open(gw2efficiencyurl,new=2)
webbrowser.open(gw2crafturl+'#'+tier)
