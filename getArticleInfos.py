import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import re
from Utils import *
def getArticleInfos(soup):
	hdr = {'User-Agent':'Mozilla/5.0'}
	infos = ['contentID', 'writerName', 'writerSignInDate', 'writerSignInDate', 'writerVisitingCount',
			'recommendCount', 'viewCount', 'memoCount' , 'postTime', 'normalPostCount', 'bestPostCount', 'BOBPostCount',
			'board', 'title', 'changjakOption', 'permOption', 'prohibitBestOption', 'prohibitBOBOption', 'prohibitBoninOption', 
			'prohibitOutsidePermOption', 'imgCount', 'videoCount',  'youtubeCount', 'textLineCount', 
			'bestTime','BoBTime','okTime', 'memoTime']

	## get Writer Infomation
	writerInfoContents = soup.find_all("div", class_="writerInfoContents")
	divTags = writerInfoContents[0].find_all("div")

	contentID = divTags[0].text.split(' : ')[1]
	writerName = (divTags[1].find_all("b"))[0].text   # 글쓴이 닉네임
	writerInfo_ = (divTags[1].find_all("span"))[-1].text
	writerSignInDate = re.split(':| |\)',writerInfo_)[1]   # 글쓴이 가입 날짜
	writerVisitingCount = re.split(':| |\)',writerInfo_)[3]  # 방문 횟수
	recommendCount = divTags[2].find_all("span")[0].text   # 추천수
	viewCount = divTags[3].text.split(' : ')[1]			# 조회수 
	memoCount = re.split(' : |개',divTags[5].text)[1]   # 댓글 수 
	# BOBTime = divTags[6].text.split(' : ')[1]			  # 베스트 등록 시간
	postTime = divTags[6].text.split(' : ')[1]			 # 게시 시간

	#### 게시자의 다른 글 개수 ####
	baseURL = "http://www.todayhumor.co.kr/board/"
	writerProfileURLSuffix = divTags[1].find_all("a")[0]["href"]
	writerProfileURL = baseURL + writerProfileURLSuffix
	writerProfileReq = urllib.request.Request(writerProfileURL,headers=hdr)

	writerProfileDoc = ""
	with urllib.request.urlopen(writerProfileReq) as url:
		writerProfileDoc = url.read()

	writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")	
	table_list = writerProfileSoup.find_all("table", class_="table_list")
	normalPostCount = table_list[0].find("a").text		 # 유저가 쓴 글 개수
	#try: # 차단유
	#	normalPostCount = table_list[0].find("a").text		 # 유저가 쓴 글 개수
	#except:
	#	normalPostCount = 0 
		

	baseURL = "http://www.todayhumor.co.kr"
	member_menu_box = writerProfileSoup.find_all("div", class_="member_menu_box")
	writerProfileURLs = member_menu_box[0].find_all("a")
	writerProfileBestURL = baseURL + writerProfileURLs[1]["href"]
	writerProfileBOBURL = baseURL + writerProfileURLs[2]["href"]

	writerProfileReq = urllib.request.Request(writerProfileBestURL,headers=hdr)
	writerProfileDoc = ""
	with urllib.request.urlopen(writerProfileReq) as url:
		writerProfileDoc = url.read()

	writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")	
	table_list = writerProfileSoup.find_all("table", class_="table_list")
	bestPostCount = table_list[0].find("a").text			# 유저가 쓴 베스트 개수

	writerProfileReq = urllib.request.Request(writerProfileBOBURL,headers=hdr)
	writerProfileDoc = ""
	with urllib.request.urlopen(writerProfileReq) as url:
		writerProfileDoc = url.read()

	writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")	
	table_list = writerProfileSoup.find_all("table", class_="table_list")
	BOBPostCount = table_list[0].find("a").text			 # 유저가 쓴 베오베 개수
	################################

	## get Bulletin board Info
	viewSubjectDiv = soup.find_all("div", class_="viewSubjectDiv")

	board = viewSubjectDiv[0].find_all("span")[0]["class"][1]	# 게시판 이름 
	title = viewSubjectDiv[0].find_all("div")[0].text.strip()		 # 제목

	## post option : 창작글, 펌글, 베스트 금지, 베오베 금지, 본인삭제금지, 외부펌 금지
	contentContainer = soup.find_all("div", class_="contentContainer")
	postOption = contentContainer[0].find_all("table")

	changjakOption = False # 창작글
	permOption = False # 펌글
	prohibitBestOption = False # 베스트 금지
	prohibitBOBOption = False # 베오베 금지
	prohibitBoninOption = False # 본인삭제 금지
	prohibitOutsidePermOption = False # 외부펌 금지


	if len(postOption) is 2 :  # 첫 <table>은 글 옵션 두번째 <table>은 출처. 즉 테이블이 1개이면 출처만 있고 옵션이 없음

		options = postOption[0].find_all("li")

		for option in options : 
			optionName = option.find_all("div")[1].text
			if optionName == "창작글" :
				changjakOption = True
			elif optionName == "펌글" :
				permOption = True
			elif optionName == "베스트금지" :
				prohibitBestOption = True
			elif optionName == "베오베금지" :
				prohibitBOBOption = True
			elif optionName == "본인삭제금지" :
				prohibitBoninOption = True
			elif optionName == "외부펌금지" :
				prohibitOutsidePermOption = True	

	## 본문 내용 가져오기
	# 구해야 할것 :  이미지 개수, 동영상 유무(youtube or 움짤), 텍스트 길이, 키워드

	viewContent = soup.find_all("div", class_="viewContent")
	imgs = viewContent[0].find_all("img") # 본문 삽입된 이미지들
	videos = viewContent[0].find_all("video")
	youtubes = viewContent[0].find_all("iframe")
	texts = viewContent[0].find_all("div")

	textData = []
	for text in texts :
		if (text.text) :
			textData.append(text.text)

	imgCount = len(imgs)   # 이미지 카운트
	videoCount = len(videos)   # 움짤 카운트
	youtubeCount = len(youtubes)   # 유투브(iframe) 개수
	textLineCount = len(textData)   # 텍스트 줄 수

	okList = getOkList(soup)
	postTime_ = datetime.strptime(postTime, '%Y/%m/%d %H:%M:%S')
	okTime = list(map(lambda x: (x - postTime_).total_seconds(), okList))
	bestTime, BoBTime, memoList = getMemoList(soup)
	memoTime = list(map(lambda x: (x - postTime_).total_seconds(), memoList))

	import collections
	articleInfo = collections.OrderedDict.fromkeys(infos)
	for entity in infos:
		exec("articleInfo['{}'] = {}".format(entity, entity))

	return articleInfo
