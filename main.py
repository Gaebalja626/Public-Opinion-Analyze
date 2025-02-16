import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

import use_db

options = Options()

def load_driver():
    service = Service()

    options = webdriver.ChromeOptions()
    options.add_argument("headless")

    driver = webdriver.Chrome(service=service, options=options)

    return driver

# TODO 6개 대분야에서 상위 n개 뉴스의 url을 크롤링해오는 코드 작성 필요
def get_html(driver, url, wait_time=5):
    driver.implicitly_wait(wait_time)
    driver.get(url)

    html = driver.execute_script("return document.documentElement.outerHTML;")

    return html

def parse_article(html):
    soup = BeautifulSoup(html, 'lxml')

    article_title = soup.select_one('div.media_end_head_title').text.strip()
    reporter_name = soup.select_one('em.media_end_head_journalist_name').text.strip()
    datestamp = soup.select_one('div.media_end_head_info_datestamp_bunch').text.strip()
    article = soup.select_one('div#newsct_article').text.strip()
    journal = soup.select_one('a.media_end_head_top_logo').text.strip()
    # TODO 공감수 파싱
    # TODO 기사id url에서 파싱 - 이 때 언론사id+언론사 내에서 기사id인 거 같아서 뒤에 통째로 잘라 와야 할 듯

    res_article = [article_title, reporter_name, datestamp, article, journal]

    return res_article

def parse_comment(driver, url, wait_time=5, delay_time=0.5):
    driver.get(url)
    driver.implicitly_wait(wait_time)

    while True:
        try:
            more = driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
            more.click()
            time.sleep(delay_time)

        except:
            break

    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    nicknames = soup.select('span.u_cbox_nick')
    list_nicknames = [nickname.text for nickname in nicknames]

    datetimes = soup.select('span.u_cbox_date')
    list_datetimes = [datetime.text for datetime in datetimes]

    contents = soup.select('span.u_cbox_contents')
    list_contents = [content.text for content in contents]

    res_comment = list(zip(list_nicknames, list_datetimes, list_contents))
    # TODO 답글 크롤링 그리고 댓글 id

    return res_comment

if __name__ == '__main__':
    driver = load_driver()

    try:
        url = 'https://n.news.naver.com/mnews/article/081/0003518095'
        html = get_html(driver, url)

        res_article_list = parse_article(html)
        res_comment_list = parse_comment(driver, url.replace('/article/', '/article/comment/'))

        print("/// ARTICLE ///")
        print(res_article_list)
        print("/// COMMENT ///")
        print(res_comment_list)

    finally:
        driver.quit()

    # TODO db에 추가 (sqlite)
