import requests
from bs4 import BeautifulSoup

#책 제목 가져오기 함수
def book_title(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/category/index.nhn?cate_code=130050&tab=top100&list_type=list&sort_type=publishday&page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.category_section.category_section2 > ol.basic.top100 > li")
        for tr in trs:
            title = tr.select_one("dl > dt").text.replace('\n',"")     
            results.append(title)  
    return results

#print(book_title(1,2))


#책 저자 가져오기 함수
def book_writer(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/category/index.nhn?cate_code=130050&tab=top100&list_type=list&sort_type=publishday&page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.category_section.category_section2 > ol.basic.top100 > li")
        for tr in trs:
            writer = tr.select_one("dl > dd > a").text
            results.append(writer)  
    return results
#print(book_writer(1,2))


# 책 표지 함수
def book_photo(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/category/index.nhn?cate_code=130050&tab=top100&list_type=list&sort_type=publishday&page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.category_section.category_section2 > ol.basic.top100 > li")
        for tr in trs:
            photo = tr.select_one("div.thumb.type_best > div.thumb_type.thumb_type2 > a > img")["src"]
            results.append(photo)  
    return results
#print(book_photo(1,2))
