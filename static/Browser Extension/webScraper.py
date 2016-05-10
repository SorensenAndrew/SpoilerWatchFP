__author__ = 'AndrewSorensen'

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import re
import random

#Gets internal links on page
def getInternallinks(bsObj, includeUrl):
    internallinks = []
    for link in bsObj.findAll("a",
                              href=re.compile("^(\/|.*(http:\/\/)"+includeUrl+")).*")):
                              if link.attrs['href'] is not None:
                                  if link.attrs['href'] not in internallinks:
                                      internallinks.append(link.attrs['href'])
    return internallinks

#Gets external links

def getExternallinks(bsObj, url):
    excludeUrl = getDomain(url)
    externallinks = []
    for link in bsObj.findAll("a",
                              href=re.compile("^(http)((?!"+excludeUrl+").)*$")):
        if link.attrs['href'] is not None and len(link.attrs['href']) != 0:
            if link.attrs['href'] not in externallinks:
                externallinks.append(link.attrs['href'])
    return externallinks

def getDomain(address):
    return urlparse(address).netloc

def followExternalOnly(bsObj, url):
    externallinks = getExternallinks(bsObj, url)
    if len(externallinks) == 0:
        print("Only internal links here")
        internallinks = getInternallinks(bsObj, getDomain(url))
        randInternallink = "http://"+getDomain(url)
        randInternallink += internallinks[random.randint(0, len(internallinks)-1)]
        bsObj = BeautifulSoup(urlopen(randInternallink))
        followExternalOnly(bsObj, randInternallink)
    else:
        randomExternal = externallinks[random.randint(0, len(externallinks)-1)]
        try:
            nextBsObj = BeautifulSoup(urlopen(randomExternal))
            print(randomExternal)
            followExternalOnly(nextBsObj, randomExternal)
        except HTTPError:
            print("Encountered error at "+randomExternal)
            followExternalOnly(bsObj, url)
url = "http://yahoo.com"
bsObj = BeautifulSoup(urlopen(url))
followExternalOnly(bsObj, url)