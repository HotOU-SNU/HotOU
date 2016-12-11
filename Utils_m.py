import numpy as np
import urllib.request
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime

def getSoup(url, parser):
    hdr = {'User-Agent':'Mozilla/5.0'}
    req = urllib.request.Request(url,headers=hdr)
    with urllib.request.urlopen(req) as url:
        doc = url.read()
    return BeautifulSoup(doc, parser)

# def getMetaData(url):
    

def getOkList(soup, isPC = 1):
    okListTime = []
    p = re.compile('\d\d\d\d/\d\d/\d\d \d\d:\d\d:\d\d')
    if isPC:
        okList = p.findall(soup.find_all("script")[0].text) #PC:0, Mobile:-1
    else:
        okList = p.findall(soup.find_all("script")[-1].text) #PC:0, Mobile:-1
    okListTime = list(map(lambda x: datetime.strptime(x, '%Y/%m/%d %H:%M:%S'), okList ))
    return okListTime
  


def getMemoList(soup, isPC = 1):
    p = re.compile('parent_table = ".*?"')
    if isPC:
        script = soup.find_all("script")[0]     #PC:0, Mobile:-1
    else:
        script = soup.find_all("script")[-1]    #PC:0, Mobile:-1
    p = p.search(script.text)
    parent_table = script.text[p.start():p.end()]
    parent_table = parent_table[16:-1]

    p = re.compile('parent_id = ".*?"')
    p = p.search(script.text)
    parent_id = script.text[p.start():p.end()]
    parent_id = parent_id[13:-1]
    memo_url = "/board/ajax_memo_list.php?parent_table=" + parent_table + "&parent_id=" + parent_id;
    memo_url = 'http://www.todayhumor.co.kr' + memo_url
#     print(memo_url)

    memo_soup =  getSoup(memo_url, "html.parser")
#     memoData = dict()
    memoList = []
    memos = json.loads(memo_soup.text)['memos']
    bestTime = 0
    BoBTime  = 0
    for memo in memos:
        if 'MOVE_HUMORBEST' in memo['memo']:
            #bestTime = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
            bestTime = memo['date']
        elif 'MOVE_BESTOFBEST' in memo['memo']:
            #BoBTime = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
            BoBTime = memo['date']
        else:
            date = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
            memoList.append(date)
#             date = memo['date']
#             memoData[date] = [int(memo['ok']), int(memo['nok'])]
    return (bestTime, BoBTime, memoList)
#     json.loads(memo_soup.text)['memos']


import linecache
import sys

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

