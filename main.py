import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

import json

import use_db

options = Options()


def load_driver():
    service = Service()

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_experimental_option('detach', True)

    driver = webdriver.Chrome(service=service, options=options)

    return driver


# TODO 6개 대분야에서 상위 n개 뉴스의 url을 크롤링해오는 코드 작성 필요
def get_html(driver, url, wait_time=5):
    driver.implicitly_wait(wait_time)
    driver.get(url)

    html = driver.execute_script("return document.documentElement.outerHTML;")

    return html


def parse_article(html, article_id):
    soup = BeautifulSoup(html, 'lxml')

    article_id = article_id
    article_title = soup.select_one('div.media_end_head_title').text.strip()
    reporter_name = soup.select_one('em.media_end_head_journalist_name').text.strip()
    datestamp = soup.select_one('div.media_end_head_info_datestamp_bunch').text.strip()
    article = soup.select_one('div#newsct_article').text.strip()
    journal = soup.select_one('a.media_end_head_top_logo').text.strip()

    # TODO 리액션 정보 가져오는 게 안 돼요.
    # TRY1 / 그냥 냅다 크롤링 -> 0으로만 나옴. 뉴스 소스코드(mnews/article/081에 있는 코드의 419번줄부터) 살펴보니까 0으로 채워져있음.
    # 그냥 간단히 html코드에서 크롤링하는 거로는 안 되는 거 같음.
    # 로딩 시간 기다려보기+셀레니움 동적 크롤링하는 거 직접 봐도 로딩된 상태였음에도 0으로 가져옴.

    # TRY2 / api 요청해보기 -> send_request()와 아래 코드가 해당 시도의 흔적..
    # 아래는 리액션 라벨 이름만 응답이 오고 그래서 다른 api로 하면 될까 싶어서 크롬 dev tool로 네트워크 관찰해봤는데도
    # 직접적으로 리액션 카운트 값을 보내주는 게 일단 나는 못 찾음......
    # 직접 그 카운트를 변경시키면 관련된 내역이 뜨긴 하는데 이거는 보안 그런 게 잘 되어있어서 접근하기가 쉽지 않아보임.

    # reactions_json = send_request(
    #     api_url="https://news.like.naver.com/v1/search/contents",
    #     params={
    #         "suppress_response_codes": "true",
    #         "q": f"NEWS[{article_id}]",
    #         "isDuplication": "false"
    #     },
    #     headers={
    #         "referer": "https://n.news.naver.com/",
    #         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    #         "authority": "news.like.naver.com",
    #         "accept": "*/*",
    #         "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    #     }
    # )
    # print(reactions_json)
    # reactions = json.loads(reactions_json['contents'][0]['contents'][0]['reactionCount'])

    res_article = [article_id, article_title, reporter_name, datestamp, article, journal]

    return res_article

# def send_request(api_url, params, headers):
#     import requests
#
#     response = requests.get(api_url, params=params, headers=headers)
#     print(response)
#     print('////////')
#     json_data = response.json()
#
#     return json_data

def load_comment(driver, url, wait_time=5, delay_time=0.5):
    driver.get(url)
    driver.implicitly_wait(wait_time)

    while True:
        try:
            more = driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
            more.click()
            time.sleep(delay_time)
        except:
            break

    reply_cnts = driver.find_elements(By.CLASS_NAME, 'u_cbox_reply_cnt')
    actions = ActionChains(driver)

    for reply_cnt in reply_cnts:
        cnt_txt = reply_cnt.text.strip()
        cnt = int(cnt_txt) if cnt_txt.isdigit() else 0

        if cnt>0:
            reply_btn = reply_cnt.find_element(By.XPATH, "./parent::*")
            actions.move_to_element(reply_btn).click().perform()
            time.sleep(delay_time)

    html = driver.page_source

    return html


def parse_comment(html):
    soup = BeautifulSoup(html, 'lxml')

    nicknames = soup.select('span.u_cbox_nick')
    list_nicknames = [nickname.text for nickname in nicknames]

    datetimes = soup.select('span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]

    contents = soup.select('span.u_cbox_contents')
    list_contents = [content.text for content in contents]

    # TODO 댓글 id 크롤링
    # TODO 댓글 찬반 개수 크롤링

    res_comment = list(zip(list_nicknames, list_datetimes, list_contents))


    return res_comment

if __name__ == '__main__':
    driver = load_driver()

    try:
        url = 'https://n.news.naver.com/mnews/article/081/0003518494'
        html = get_html(driver, url)

        press_id, article_num = url.split('article/')[1].split('/')
        article_id = f'{press_id}_{article_num}'

        res_article_list = parse_article(html, article_id)
        res_comment_list = parse_comment(driver, url.replace('/article/', '/article/comment/'))

        print("/// ARTICLE ///")
        print(res_article_list)
        print("/// COMMENT ///")
        print(res_comment_list)

    finally:
        driver.quit()

    # TODO db에 추가 (sqlite)
