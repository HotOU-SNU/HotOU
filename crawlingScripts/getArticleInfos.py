import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import re
from Utils import *
import time
from Utils_m import PrintException
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

def getArticleInfos_m(soup):

    try:
        hdr = {'User-Agent':'Mozilla/5.0'}
        start = time.time()
        infos = ['contentID', 'writerName', 'writerSignInDate', 'writerSignInDate', 'writerVisitingCount',
                'recommendCount', 'viewCount', 'memoCount' , 'postTime', 'normalPostCount', 'bestPostCount', 'BOBPostCount',
                'board', 'title', 'changjakOption', 'permOption', 'prohibitBestOption', 'prohibitBOBOption', 'prohibitBoninOption',
                'prohibitOutsidePermOption', 'imgCount', 'videoCount',  'youtubeCount', 'textLineCount', 
                'bestTime','BoBTime','okTime', 'memoTime']

## get Writer Infomation
        writerInfoContents = soup.find("div", class_="view_spec")
        spanTags = writerInfoContents.find_all("span")

        contentID = writerInfoContents.find("span", class_="view_no").text
        writerName = writerInfoContents.find("span", class_="view_writer").text   # 글쓴이 닉네임
        if ':' in spanTags[5].text:   # 작성자 아이콘에 따라 span 위치가 바뀜
            writerInfo = spanTags[5].text
        else :
            writerInfo = spanTags[6].text
        writerSignInDate = re.split(':| |\)',writerInfo)[1]   # 글쓴이 가입 날짜
        writerVisitingCount = re.split(':| |\)',writerInfo)[3]  # 방문 횟수

        recommendCount = writerInfoContents.find("span", class_="view_okNok").text   # 추천수
        viewCount = writerInfoContents.find("span", class_="view_viewCount").text[0:-1]         # 조회수 
        memoCount = writerInfoContents.find("span", class_="view_replyCount").text[0:-1]   # 댓글 수 
# BOBTime = divTags[6].text.split(' : ')[1]           # 베스트 등록 시간
        if writerInfoContents.find("span", class_="view_wdate") :     # 베스트 OR 베오베
            postTime = writerInfoContents.find("span", class_="view_wdate").text           # 게시 시간
        else :                                                        # 일반글
            postTime = writerInfoContents.find("span", class_="view_bestRegDate").text

        #print (time.time() - start)

#### 게시자의 다른 글 개수 ####
        baseURL = "http://m.todayhumor.co.kr"
        writerProfileURLSuffix = writerInfoContents.find("span", class_="view_writer").find("a")["href"]
        writerProfileURL = baseURL + writerProfileURLSuffix
        writerProfileReq = urllib.request.Request(writerProfileURL,headers=hdr)
        writerProfileDoc = urllib.request.urlopen(writerProfileReq, timeout=5).read()
        writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")  

        normalPostCount = writerProfileSoup.find("span", class_="list_no").text      # 유저가 쓴 글 개수

        writerProfileBestURL = writerProfileURL + '&member_kind=humorbest'
        writerProfileBOBURL = writerProfileURL + '&member_kind=bestofbest'

        writerProfileReq = urllib.request.Request(writerProfileBestURL,headers=hdr)
        writerProfileDoc = urllib.request.urlopen(writerProfileReq, timeout=5).read()
        writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")  

        bestPostCount = 0
        best_list_no = writerProfileSoup.find("span", class_="list_no")
        if best_list_no :
            bestPostCount = best_list_no.text           # 유저가 쓴 베스트 개수

        writerProfileReq = urllib.request.Request(writerProfileBOBURL,headers=hdr)
        writerProfileDoc = urllib.request.urlopen(writerProfileReq, timeout=5).read()
        writerProfileSoup = BeautifulSoup(writerProfileDoc, "html.parser")  

        BOBPostCount = 0
        BOB_list_no = writerProfileSoup.find("span", class_="list_no")
        if BOB_list_no :
            BOBPostCount = BOB_list_no.text         # 유저가 쓴 베오베 개수


## get Bulletin board Info
        view_title = soup.find("div", class_="view_title")

        board = view_title.find("a")["href"].split("=")[1]  # 게시판 이름 
        title = view_title.find("span", class_="view_subject").text.strip()      # 제목

## post option : 창작글, 펌글, 베스트 금지, 베오베 금지, 본인삭제금지, 외부펌 금지
        postOption = soup.find("table")

        changjakOption = False # 창작글
        permOption = False # 펌글
        prohibitBestOption = False # 베스트 금지
        prohibitBOBOption = False # 베오베 금지
        prohibitBoninOption = False # 본인삭제 금지
        prohibitOutsidePermOption = False # 외부펌 금지

        if postOption :
            options = postOption.find_all("li")

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

        viewContent = soup.find("div", class_="view_content")
        imgs = viewContent.find_all("img") # 본문 삽입된 이미지들
        videos = viewContent.find_all("video")
        youtubes = viewContent.find_all("iframe")
        texts = viewContent.find_all("div")

        textData = []
        if soup.find_all("img", {"src":"images/list_icon_mobile.gif"}) :  # 휴대에서 쓴 게시글
            texts = viewContent.findAll('br')
            if(viewContent.text) :
                if(texts and texts[0].previousSibling and texts[0].previousSibling.strip()):
                    textData.append(texts[0].previousSibling)
                else :
                    textData.append(viewContent.text)
            for text in texts:
                if text and text.nextSibling : 
                    textData.append(text.nextSibling)
        else :
            texts = viewContent.find_all("div")
            if(viewContent.text) :
                if(texts and texts[0].previousSibling and texts[0].previousSibling.strip()):
                    textData.append(texts[0].previousSibling.strip())
                else :
                    textData.append(viewContent.text)
            for text in texts :
                newtext = text.text.replace("&nbsp", "").strip()
                if (newtext) :
                    textData.append(newtext)
            texts = viewContent.find_all("span")
            for text in texts :
                newtext = text.text.replace("&npsp", "").strip()
                if (newtext) :
                    textData.append(newtext)

        imgCount = len(imgs)   # 이미지 카운트
        videoCount = len(videos)   # 움짤 카운트
        youtubeCount = len(youtubes)   # 유투브(iframe) 개수
        textLineCount = len(textData)   # 텍스트 줄 수

        #print (time.time() - start)


        okList = getOkList(soup, isPC = 0)
        postTime_ = datetime.strptime(postTime, '%Y/%m/%d %H:%M:%S')
        okTime = list(map(lambda x: (x - postTime_).total_seconds(), okList))
        bestTime, BoBTime, memoList = getMemoList(soup, isPC = 0)
        memoTime = list(map(lambda x: (x - postTime_).total_seconds(), memoList))

        #print (time.time() - start)


        import collections
        articleInfo = collections.OrderedDict.fromkeys(infos)
        for entity in infos:
            exec("articleInfo['{}'] = {}".format(entity, entity))

    #print (time.time() - start)
    except :
        PrintException()


    return articleInfo

