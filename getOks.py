import numpy as np
from Utils import *
import time

article_no = np.random.randint(226700, 288325, size=200)

dbForOk = dict()
start = time.time()
for i in article_no:
    url = 'http://m.todayhumor.co.kr/view.php?table=bestofbest&no={}'.format(i)
    soup = getSoup(url, 'html.parser')
    if not len(soup.find_all('title')): continue
    okList = getOkList(soup, isPC = 0)
    postTime = datetime.strptime(soup.find_all('span', class_="view_wdate")[0].text, '%Y/%m/%d %H:%M:%S')
    okTime = list(map(lambda x: (x - postTime).total_seconds(), okList[:50]))
    dbForOk[i] = okTime
end = time.time()
print(end-start)

import pickle as pkl
with open('db_bob_oks1.pkl', 'wb') as f:
    pkl.dump(dbForOk, f)
