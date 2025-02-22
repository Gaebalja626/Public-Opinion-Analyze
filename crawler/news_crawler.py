import time
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from crawler_utils import load_driver, get_soup


class NaverNewsCrawler:
    def __init__(self, url: str):
        """
        네이버 뉴스 크롤러 초기화
        Args:
            url: 크롤링할 뉴스 기사 URL
        """
        self.url = url
        self.driver = load_driver()
        self.article_soup = get_soup(url)
        self.comment_html = None

        self.journal_id, article_num = url.split('article/')[1].split('/')
        self.article_id = f'{self.journal_id}_{article_num}'

    def crawl(self) -> Tuple[List, List]:
        """
        뉴스 기사와 댓글을 크롤링
        Returns:
            기사 정보와 댓글 정보를 포함하는 튜플
        """
        try:
            # 댓글 HTML 가져오기
            comment_url = self.url.replace('/article/', '/article/comment/')
            self.comment_html = self._get_comment_html(comment_url)

            # 기사와 댓글 파싱
            article_data = self._parse_article()
            comment_data = self._parse_comment()

            return article_data, comment_data

        finally:
            self.driver.quit()

    def _parse_article(self) -> List:
        """
        뉴스 기사 내용을 파싱
        Returns:
            기사 정보를 담은 리스트
            기사 id, 제목, 언론사, 기자 id, 발행 날짜, 수정 날짜, 기사 내용
        """
        soup = self.article_soup

        article_title = soup.select_one('div.media_end_head_title').text.strip()
        journalist_id = soup.select_one('a.media_end_head_journalist_box')['href'][-5:]
        # 저널명이나 기자이름은 따로 그 전용페이지 가서 또 크롤링해오는 게 나을 거 같긴 한데 일단 남겨둠.
        # journal = soup.select_one('a.media_end_head_top_logo').text.strip()
        # reporter_name = soup.select_one('em.media_end_head_journalist_name').text.strip()
        datetime = soup.select_one('span._ARTICLE_DATE_TIME').text.strip()
        modify_datetime = soup.select_one('span._ARTICLE_MODIFY_DATE_TIME').text.strip()
        article_content = soup.select_one('div#newsct_article').text.strip()

        return [
            self.article_id,
            article_title,
            self.journal_id,
            journalist_id,
            datetime,
            modify_datetime,
            article_content
        ]

    def _get_comment_html(self, url: str, wait_time=5, delay_time=0.5) -> str:
        """
        댓글 HTML을 가져오기
        Args:
            url: 댓글 페이지 URL
            wait_time: 페이지 로딩 대기 시간
            delay_time: 클릭 간 대기 시간
        Returns:
            댓글 HTML 문자열
        """
        self.driver.get(url)
        self.driver.implicitly_wait(wait_time)

        # 더보기 버튼 클릭
        while True:
            try:
                more = self.driver.find_element(By.CLASS_NAME, 'u_cbox_btn_more')
                more.click()
                time.sleep(delay_time)
            except:
                break

        # 답글 버튼 클릭
        reply_cnts = self.driver.find_elements(By.CLASS_NAME, 'u_cbox_reply_cnt')
        actions = ActionChains(self.driver)

        for reply_cnt in reply_cnts:
            cnt_txt = reply_cnt.text.strip()
            cnt = int(cnt_txt) if cnt_txt.isdigit() else 0

            if cnt > 0:
                reply_btn = reply_cnt.find_element(By.XPATH, "./parent::*")
                actions.move_to_element(reply_btn).click().perform()
                time.sleep(delay_time)

        return self.driver.page_source

    def _parse_comment(self) -> List[Tuple]:
        """
        댓글 내용을 파싱
        Returns:
            댓글 정보를 담은 리스트
        """
        soup = BeautifulSoup(self.comment_html, 'lxml')

        # nicknames = [nickname.text for nickname in soup.select('span.u_cbox_nick')]
        user_ids = []
        import re
        users_data = soup.select('a.u_cbox_btn_userblock')
        for user_data in users_data:
            user_data_param = user_data['data-param']
            match = re.search(r"idNo:'(.*?)'", user_data_param)
            user_ids.append(match.group(1))
        datetimes = [datetime.text for datetime in soup.select('span.u_cbox_date')]
        contents = [content.text for content in soup.select('span.u_cbox_contents')]
        upvotes = [upvote.text for upvote in soup.select('em.u_cbox_cnt_recomm')]
        downvotes = [downvote.text for downvote in soup.select('em.u_cbox_cnt_unrecomm')]

        return list(zip(user_ids, datetimes, contents, upvotes, downvotes))


if __name__ == '__main__':
    url = 'https://n.news.naver.com/mnews/article/081/0003518494'
    crawler = NaverNewsCrawler(url)
    article_data, comment_data = crawler.crawl()

    print("/// ARTICLE ///")
    print(article_data)
    print("/// COMMENT ///")
    print(comment_data)