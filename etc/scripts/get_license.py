#apt-get install python-demjson
import urllib2
import json
import requests
from bs4 import BeautifulSoup
data=[]
for i in range (0,19):
    wiki="https://www.openhub.net/licenses?page="+str(i)
    page=urllib2.urlopen(wiki)
    soup=BeautifulSoup(page,'html.parser')
    all_lic=soup.find(id="license")
    all_as=all_lic.select("table a")
    for pt in all_as:
        itr={}
        itr["openhub_url"]=pt.get("href")
        itr["name"]=pt.get_text()
        data.append(itr)
json=json.dumps(data)
print json

#output-> $ python get_license.py | jsonlint
