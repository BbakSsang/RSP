import requests
from bs4 import BeautifulSoup


def get_food(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://www.10000recipe.com/recipe/list.html?order=reco&page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("ul.rcp_m_list2 > ul.common_sp_list_ul.ea4")
        for tr in trs:
            # 음식 사진
            photo = tr.select_one("li.common_sp_list_li > div.common_sp_thumb > a.common_sp_link > img")
            # 음식 이름 
            photo = tr.select_one

            
            results.append(name)
        
    return results

#print(get_food(1,3))


def book_reco(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/bookshelf/recommendbook_list.nhn?page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.section_bookshelf > ol.basic.rank_list > li")
        for tr in trs:
            # 책 표지
            photo = tr.select_one("div.thumb.type_bookshelf > div.thumb_type > a > img")["src"]
            # 책 제목
            # title = tr.select_one("dl > dt").text.replace('\n',"")
            # # 책 저자
            # writer = tr.select_one("dl > dd.txt_block > a").text
            # # 책 출판사
            # publisher = tr.select_one("dl >dd.txt_block > span.publisher").text
            
            results.append(photo) 
            #results.append((photo, title,writer,publisher)) 
        
    return results

print(book_reco(1,10))

# 책 표지 함수
def book_photo(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/bookshelf/recommendbook_list.nhn?page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.section_bookshelf > ol.basic.rank_list > li")
        for tr in trs:
            photo = tr.select_one("div.thumb.type_bookshelf > div.thumb_type > a > img")["src"]
            results.append(photo)  
    return results
#print(book_photo(1,2))

#책 제목 가져오기 함수
def book_title(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/bookshelf/recommendbook_list.nhn?page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.section_bookshelf > ol.basic.rank_list > li")
        for tr in trs:
            title = tr.select_one("dl > dt").text.replace('\n',"")
            results.append(title)  
    return results
#print(book_title(1,2))

#책 저자 가져오기 함수
def book_writer(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/bookshelf/recommendbook_list.nhn?page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.section_bookshelf > ol.basic.rank_list > li")
        for tr in trs:
            writer = tr.select_one("dl > dd.txt_block > a").text
            results.append(writer)  
    return results
# print(book_writer(1,2))

# 책 출판사 가져오기 함수
def book_publisher(start,end=1):
    results = []
    for i in range(start, end+1):
        url = 'https://book.naver.com/bookshelf/recommendbook_list.nhn?page={}'.format(i)
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")
        trs = bs.select("div.section_bookshelf > ol.basic.rank_list > li")
        for tr in trs:
            publisher = tr.select_one("dl >dd.txt_block > span.publisher").text
            results.append(publisher)  
    return results
#print(book_publisher(1,2))