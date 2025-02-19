import time
from typing import List, Tuple

from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

from .crawler_utils import load_driver, get_soup


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

        # URL에서 article_id 추출
        press_id, article_num = url.split('article/')[1].split('/')
        self.article_id = f'{press_id}_{article_num}'

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
        """
        soup = self.article_soup

        article_title = soup.select_one('div.media_end_head_title').text.strip()
        journal = soup.select_one('a.media_end_head_top_logo').text.strip()
        reporter_name = soup.select_one('em.media_end_head_journalist_name').text.strip()
        datetime = soup.select_one('div.media_end_head_info_datestamp_bunch').text.strip()
        article_content = soup.select_one('div#newsct_article').text.strip()

        return [
            self.article_id,
            article_title,
            journal,
            reporter_name,
            datetime,
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

        # 각 요소 추출
        nicknames = [nickname.text for nickname in soup.select('span.u_cbox_nick')]
        datetimes = [datetime.text for datetime in soup.select('span.u_cbox_date')]
        contents = [content.text for content in soup.select('span.u_cbox_contents')]
        recomms = [recomm.text for recomm in soup.select('em.u_cbox_cnt_recomm')]
        unrecomms = [unrecomm.text for unrecomm in soup.select('em.u_cbox_cnt_unrecomm')]

        return list(zip(nicknames, datetimes, contents, recomms, unrecomms))


if __name__ == '__main__':
    url = 'https://n.news.naver.com/mnews/article/081/0003518494'
    crawler = NaverNewsCrawler(url)
    article_data, comment_data = crawler.crawl()

    print("/// ARTICLE ///")
    print(article_data)
    print("/// COMMENT ///")
    print(comment_data)