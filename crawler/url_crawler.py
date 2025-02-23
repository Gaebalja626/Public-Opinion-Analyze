from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
import time
from typing import List

from .crawler_utils import load_driver


class NaverNewsURLCrawler:
    NEWS_ID_INCREMENT = 3  # 네이버 뉴스 ID 증가값

    def __init__(self, keyword: str, query_n: int, sort_by: str):
        """
        네이버 뉴스 URL 크롤러 초기화
        Args:
            keyword: 검색할 키워드
            query_n: 크롤링할 뉴스 기사 개수
        """
        self.keyword = keyword
        self.query_n = query_n
        self.sort_by = sort_by
        self.driver = load_driver()
        self.search_url = self._build_search_url()

    def _build_search_url(self) -> str:
        """
        검색 URL 생성
        Returns:
            네이버 뉴스 검색 URL
        """
        match self.sort_by:
            case '1':# 관련도순
                return f"https://search.naver.com/search.naver?ssc=tab.news.all&where=news&query={self.keyword}"
            case '2':
                return f"https://search.naver.com/search.naver?where=news&query={self.keyword}&sm=tab_opt&sort=1&photo=0&field=0&pd=0&ds=&de=&docid=&related=0&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so%3Add%2Cp%3Aall&is_sug_officeid=0&office_category=0&service_area=0"
            case _:
                raise ValueError('올바르지 않은 입력입니다.')


    def crawl(self, wait_time=5, delay_time=0.5) -> List[str]:
        """
        뉴스 URL 크롤링
        Args:
            wait_time: 페이지 로딩 대기 시간
            delay_time: 스크롤 후 대기 시간
        Returns:
            크롤링된 뉴스 URL 리스트
        """
        try:
            news_urls = self._get_news_urls(wait_time, delay_time)
            return news_urls
        finally:
            self.driver.quit()

    def _get_news_urls(self, wait_time: int, delay_time: float) -> List[str]:
        """
        뉴스 URL 수집
        Args:
            wait_time: 페이지 로딩 대기 시간
            delay_time: 스크롤 후 대기 시간
        Returns:
            수집된 뉴스 URL 리스트
        """
        news_urls = []

        self.driver.get(self.search_url)
        self.driver.implicitly_wait(wait_time)

        while True:
            news_elements = self.driver.find_elements(By.CSS_SELECTOR, 'a.info:not(.press)')
            news_n = len(news_elements)

            if self.query_n <= news_n:
                for element in news_elements[:self.query_n]:
                    news_url = element.get_attribute('href')
                    news_urls.append(news_url)
                break

            try:
                parent_li = news_elements[-1].find_element(By.XPATH, "./ancestor::li")
                current_id = int(parent_li.get_attribute('id')[6:])

                additional_news_needed = self.query_n - news_n
                target_id = current_id + (additional_news_needed * self.NEWS_ID_INCREMENT)

                scroll_script = self._build_scroll_script(current_id, additional_news_needed)
                self.driver.execute_script(scroll_script)
                time.sleep(delay_time)

            except NoSuchElementException:
                print("스크롤할 요소를 찾을 수 없음.")
                break
            except Exception as e:
                print(f"예상치 못한 오류 발생: {e}")
                raise

        return news_urls

    def _build_scroll_script(self, current_id: int, additional_news_needed: int) -> str:
        """
        스크롤 JavaScript 코드 생성
        Args:
            current_id: 현재 마지막 뉴스의 ID
            additional_news_needed: 추가로 필요한 뉴스 개수
        Returns:
            실행할 JavaScript 코드
        """
        return f"""
            let currentElement = document.getElementById('sp_nws{current_id}');
            let currentPos = currentElement.getBoundingClientRect().top;

            let estimatedHeight = currentElement.offsetHeight;
            let numberOfBlocks = {additional_news_needed};
            let scrollAmount = currentPos + (estimatedHeight * numberOfBlocks * 1.2);

            window.scrollBy(0, scrollAmount);
        """


if __name__ == '__main__':
    keyword = input("검색하실 키워드를 입력해주세요: ")
    number = int(input("크롤링할 뉴스 기사의 개수를 입력해주세요: "))
    sort = input('정렬 기준을 선택해 숫자를 입력해 주세요. ( 1-관련도순, 2-최신순 ): ')

    crawler = NaverNewsURLCrawler(keyword, number, sort)
    news_urls_list = crawler.crawl()
    print(news_urls_list)