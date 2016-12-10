from getArticleInfos import getArticleInfos
import time
import numpy as np
from Utils import getSoup

# for sisa

#article_no = np.random.randint(643000, 814061, size=10000)
#article_no = [673581] # left user
#article_no = [706828] # banned user

article_infos = []

noArticle = 10000
i = 0
while i < noArticle:
	start = time.time()
	no = np.random.randint(643000, 814061)
	#no = 698234 # blind
	#no = 795305 # deleted

	url = 'http://www.todayhumor.co.kr/board/view.php?table=sisa&no={}'.format(no)
	soup = getSoup(url, 'html.parser')
	#isArticle = soup.find_all('title')
	#if '불편을 드려서' in soup.text:
	#	print('banned from OU')
	#	break
	#if '현재 블라인드 상태인 게시물입니다.' in soup.text:
	#	print('blined article')
	#	continue
	#if '해당 게시물이 존재하지 않습니다' in soup.text:
	#	print('deleted article')
	#	continue
	try:
		article_infos.append(getArticleInfos(soup))
	except:
		continue
	end = time.time()
	print('[%5d]: %d took %f'%(i,no,end-start))
	i = i + 1
#print(article_infos)

import pickle as pkl
with open('sisa_db.pkl', 'wb') as f:
    pkl.dump(article_infos, f)
print('crawling %d articles is done'%(noArticle))
