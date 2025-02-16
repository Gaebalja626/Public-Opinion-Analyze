# step1. 관련 패키지 및 모듈 불러오기

import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# from webdriver_manager.chrome import ChromeDriverManager
import use_db

options = Options()


# step2. 네이버 뉴스 댓글정보 수집 함수
def get_naver_news_comments(url, wait_time=5, delay_time=0.1):
    options = webdriver.ChromeOptions()
    # 창 숨기는 옵션 추가
    options.add_argument("headless")
    # 크롬 드라이버로 해당 url에 접속
    print("크롬 드라이버 로드중")
    driver = webdriver.Chrome(options=options)
    print("크롬 드라이버 로드 완료")
    print("url 접속중")
    # (크롬)드라이버가 요소를 찾는데에 최대 wait_time 초까지 기다림 (함수 사용 시 설정 가능하며 기본값은 5초)
    driver.implicitly_wait(wait_time)
    print("url 접속 완료")
    # 인자로 입력받은 url 주소를 가져와서 접속
    # 1. 뉴스 링크로 들어가서 뉴스 기사를 들고오고
    # 2. 댓글 더보기 창으로 들어가서 댓글을 들고오기!!

    # 1. 뉴스 url을 상정!!
    driver.get(url)
    html = driver.execute_script("return document.documentElement.outerHTML;")

    # BeautifulSoup으로 파싱
    soup = BeautifulSoup(html, 'lxml')

    article_title = soup.select_one('div.media_end_head_title').text.strip()

    reporter_name = soup.select_one('em.media_end_head_journalist_name').text.strip()

    datestamp = soup.select_one('div.media_end_head_info_datestamp_bunch').text.strip()

    # 기사 본문 추출
    article = soup.select_one('div#newsct_article').text.strip()


    # reactions = soup.find_all('li', class_='u_likeit_list')
    # reaction_labels = []
    # reaction_counts = []
    # # 결과 수집 및 출력
    # for reaction in reactions:
    #     label = reaction.find('span', class_='u_likeit_list_name _label').text.strip()
    #     count = reaction.find('span', class_='u_likeit_list_count _count').text.strip()
    #     print(f"{label}: {count}")
    #     reaction_labels.append(label)
    #     reaction_counts.append(int(count))

    journal = soup.select_one('div.copyright').text.strip()
    journal = (journal.split("."))[0].replace("Copyright ⓒ ", "")
    # 지금까지 추출한거
    # article_title
    # datestamp
    # reporter_name
    # article
    # reaction_labels
    # reaction_counts

    article_df = pd.DataFrame({"제목": [article_title], "작성시점": [datestamp],
                               "기자이름": [reporter_name], "본문": [article],
                               "언론사": [journal], "URL": [url]})
    print("기사 크롤링 완료")
    print("[크롤링] 기사 정보")
    print(f"기사 제목 :\t {article_title}")
    _article = article.replace("\n", "").replace("\t", "")
    print(f"기사 본문 :\t {_article}")
    print(f"기자 이름 :\t {reporter_name}")
    print(f"작성 시점 :\t {datestamp}")
    print(f"언론 이름 :\t {journal}")
    print(f"URL :\t {url}")

    # 2. 댓글 처리
    # 댓글주소로 변환해서 접속
    comment_url = url.replace('/article/', '/article/comment/')
    driver.get(comment_url)
    driver.implicitly_wait(wait_time)
    print("댓글 크롤링 시작")
    # 더보기가 안뜰 때 까지 계속 클릭 (모든 댓글의 html을 얻기 위함)
    while True:

        # 예외처리 구문 - 더보기 광클하다가 없어서 에러 뜨면 while문을 나감(break)
        try:
            more = driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
            more.click()
            time.sleep(delay_time)

        except:
            break

    # 본격적인 크롤링 타임

    # selenium으로 페이지 전체의 html 문서 받기
    html = driver.page_source

    # 위에서 받은 html 문서를 bs4 패키지로 parsing
    soup = BeautifulSoup(html, 'lxml')

    # 1)작성자
    nicknames = soup.select('span.u_cbox_nick')
    list_nicknames = [nickname.text for nickname in nicknames]

    # 2)댓글 시간
    datetimes = soup.select('span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]

    # 3)댓글 내용
    contents = soup.select('span.u_cbox_contents')
    list_contents = [content.text for content in contents]

    # 4)작성자, 댓글 시간, 내용을 셋트로 취합
    res_comment = list(zip(list_nicknames, list_datetimes, list_contents))

    # 드라이버 종료
    driver.quit()

    col = ['작성자', '시간', '내용']
    # pandas 데이터 프레임 형태로 가공
    comment_df = pd.DataFrame(res_comment, columns=col)

    print("[크롤링] 댓글 정보")
    print(comment_df.head())
    return article_df, comment_df



if __name__ == '__main__':
    # 크롤링을 할 때 이 url을 직접 입력해서 사용
    url = 'https://n.news.naver.com/mnews/article/081/0003518095'

    # 뉴스 크롤링
    article_df, comment_df = get_naver_news_comments(url)

    # 데이터 베이스에 추가
    use_db.insert_article_and_comments(article_df, comment_df)
