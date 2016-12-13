from getArticleInfos import getArticleInfos, getArticleInfos_m
import time
import numpy as np
from Utils import getSoup
import pickle as pkl
import sys
import urllib.request

boards = {
    'sisa': [643000, 814061],
    'humordata': [1491211, 1691212],
    'freeboard': [1221155, 1437159],
    'star': [343816, 388818],
    'beauty': [40137, 92137]
}    

#article_no = np.random.randint(643000, 814061, size=10000)
#article_no = [673581] # left user
#article_no = [706828] # banned user

if len(sys.argv) != 3:
    print("Usage: python crawlingOU.py [board] [No]")
    exit(1)

board = sys.argv[1]
noArticle = int(sys.argv[2])
bound = boards[board]

article_infos = []
i = 0
while i < noArticle:
    start = time.time()
    no = np.random.randint(*boards[board])
    #no = 673581
    #url = 'http://www.todayhumor.co.kr/board/view.php?table={}&no={}'.format(board, no)
    url = 'http://m.todayhumor.co.kr/view.php?table={}&no={}'.format(board,no)
    try:
        soup = getSoup(url, 'html.parser')
        if '불편을 드려서' in soup.text:
        	print('banned from OU')
        	break
        #isArticle = soup.find_all('title')
        #if '현재 블라인드 상태인 게시물입니다.' in soup.text:
        #	print('blined article')
        #	continue
        #if '해당 게시물이 존재하지 않습니다' in soup.text:
        #	print('deleted article')
        #	continue
        article_infos.append(getArticleInfos_m(soup))
    except urllib.error.URLError:
        print("Timeout : Server can't respond")
        break
    except Exception as e:
        print(no)
        continue
    end = time.time()
    print('[%5d]: %d took %f'%(i,no,end-start))
    i = i + 1
    time.sleep(2)

with open('{}_db.pkl'.format(board), 'wb') as f:
    pkl.dump(article_infos, f)
print('crawling %d articles in %s is done'%(i, board))
#print(article_infos)

