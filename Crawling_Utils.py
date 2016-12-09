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


def getOkList(soup, isPC = 1):
    okListTime = []
    p = re.compile('\d\d\d\d/\d\d/\d\d \d\d:\d\d:\d\d')
    if isPC:
        okList = p.findall(soup.find_all("script")[0].text) #PC:0, Mobile:-1
    else:
        okList = p.findall(soup.find_all("script")[-1].text) #PC:0, Mobile:-1
    okListTime = list(map(lambda x: datetime.strptime(x, '%Y/%m/%d %H:%M:%S'), okList ))
    return okListTime


def getMemoList(soup):
    script = soup.find_all("script")
    p = re.compile('parent_table = ".*?"')
    p = p.search(script[0].text)
    parent_table = script[0].text[p.start():p.end()]
    parent_table = parent_table[16:-1]

    p = re.compile('parent_id = ".*?"')
    p = p.search(script[0].text)
    parent_id = script[0].text[p.start():p.end()]
    parent_id = parent_id[13:-1]
    memo_url = "/board/ajax_memo_list.php?parent_table=" + parent_table + "&parent_id=" + parent_id;
    memo_url = 'http://www.todayhumor.co.kr' + memo_url
#     print(memo_url)

    memo_soup =  getSoup(memo_url, "html.parser")
#     memoData = dict()
    memoList = []
    memos = json.loads(memo_soup.text)['memos']
    bestTime = 0
    bObTime = 0
    for memo in memos:
        if 'MOVE_HUMORBEST' in memo['memo']:
            bestTime = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
        elif 'MOVE_BESTOFBEST' in memo['memo']:
            bObTime = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
        else:
            date = datetime.strptime(memo['date'], '%Y-%m-%d %H:%M:%S')
            memoList.append(date)
#             date = memo['date']
#             memoData[date] = [int(memo['ok']), int(memo['nok'])]
    return (bestTime, bObTime, memoList)
#     json.loads(memo_soup.text)['memos']