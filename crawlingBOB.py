from bs4 import BeautifulSoup
import urllib.request
with urllib.request.urlopen("http://www.todayhumor.co.kr/board/view.php?table=bestofbest&no=287202&s_no=287202&page=1") as url:
    doc = url.read()
    soup = BeautifulSoup(doc, "html.parser")
    print(soup)
