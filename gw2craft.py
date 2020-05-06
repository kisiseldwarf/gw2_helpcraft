from bs4 import BeautifulSoup
import urllib
import json
import sys
import webbrowser

def retrieve(site, tier):
    original_list = site.find(id=tier).findAll('div')
    list_names = []
    for child in original_list:
        list_names.append(child.contents[4].text)

    list_qt = site.find(id=tier).findAll("span",{"class":"quantity"})
    return list_names,list_qt

def usage():
    print("gw2craft {tier} {job}")

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

if len(sys.argv) < 3:
    usage()
    quit()

tier = sys.argv[1]
job = sys.argv[2]

print("Retrieving items names and quantity...")
mysite = urllib.request.urlopen('https://gw2crafts.net/'+job+'.html')
soup_mysite = BeautifulSoup(mysite,features="lxml")
list_names, list_qt = retrieve(soup_mysite,tier)
list_qt = list(map(lambda x : x.text, list_qt))

print("Retrieving items id's...")
list_id = []
for child in list_names:
    list_id.append(getItemID(child))

print("Retrieving gw2efficiency URL...")
request = ""
for i in range(len(list_id)):
    if(i != len(list_id)-1):
        request = request + str(list_qt[i])+"-"+str(list_id[i])+";"
    if(i == len(list_id)-1):
        request = request + str(list_qt[i])+"-"+str(list_id[i])

gw2efficiencyurl = "https://gw2efficiency.com/crafting/calculator/a~0!b~1!c~0!d~"+request
webbrowser.open(gw2efficiencyurl,new=2)
