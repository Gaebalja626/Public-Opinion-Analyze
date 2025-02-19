from typing import Optional, Tuple, List
import logging
from datetime import datetime

from crawler.news_crawler import NaverNewsCrawler
from crawler.url_crawler import NaverNewsURLCrawler


class NaverNewsCrawlerProgram:
    def __init__(self):
        """네이버 뉴스 크롤러 프로그램 초기화"""
        self._setup_logging()

    def _setup_logging(self):
        """로깅 설정"""
        logging.basicConfig(
            filename=f'crawler_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def _print_header(self):
        """프로그램 헤더 출력"""
        print("""
        ----------------------------------------
                네이버 뉴스 크롤러 v1.0
        ----------------------------------------
        """)

    def _get_menu_choice(self) -> Optional[int]:
        """
        메뉴 선택 받기
        Returns:
            선택된 메뉴 번호 또는 None
        """
        print("""
        크롤링 방법을 선택해주세요:

        1) 네이버 뉴스 URL로 크롤링
        2) 키워드 검색으로 크롤링
        3) 종료
        """)

        try:
            choice = int(input('선택 >> '))
            if choice not in [1, 2, 3]:
                print("올바른 메뉴 번호를 입력해주세요.")
                return None
            return choice
        except ValueError:
            print("숫자로 입력해주세요.")
            return None

    def _crawl_single_url(self) -> Tuple[list, list]:
        """
        단일 URL 크롤링
        Returns:
            기사 데이터와 댓글 데이터
        """
        url = input("\nURL을 입력해주세요: ")
        logging.info(f"단일 URL 크롤링 시작: {url}")

        try:
            news_crawler = NaverNewsCrawler(url)
            return news_crawler.crawl()
        except Exception as e:
            logging.error(f"크롤링 중 오류 발생: {str(e)}")
            print(f"크롤링 중 오류가 발생했습니다: {str(e)}")
            return [], []

    def _crawl_by_keyword(self) -> List[Tuple[list, list]]:
        """
        키워드 검색 크롤링
        Returns:
            기사와 댓글 데이터 리스트
        """
        keyword = input("\n검색할 키워드를 입력해주세요: ")
        while True:
            try:
                number = int(input("크롤링할 뉴스 기사의 개수를 입력해주세요: "))
                if number <= 0:
                    print("1 이상의 숫자를 입력해주세요.")
                    continue
                break
            except ValueError:
                print("올바른 숫자를 입력해주세요.")

        logging.info(f"키워드 검색 크롤링 시작 - 키워드: {keyword}, 요청 개수: {number}")

        results = []
        try:
            url_crawler = NaverNewsURLCrawler(keyword, number)
            news_urls = url_crawler.crawl()

            for idx, news_url in enumerate(news_urls, 1):
                print(f"\n=== {idx}번째 기사 크롤링 중... ({idx}/{len(news_urls)}) ===")
                logging.info(f"기사 크롤링: {news_url}")

                try:
                    news_crawler = NaverNewsCrawler(news_url)
                    article_data, comment_data = news_crawler.crawl()
                    results.append((article_data, comment_data))
                except Exception as e:
                    logging.error(f"개별 기사 크롤링 중 오류: {str(e)}")
                    print(f"이 기사 크롤링 중 오류가 발생했습니다: {str(e)}")
                    results.append(([], []))

        except Exception as e:
            logging.error(f"URL 수집 중 오류 발생: {str(e)}")
            print(f"URL 수집 중 오류가 발생했습니다: {str(e)}")

        return results

    def _print_results(self, article_data: list, comment_data: list):
        """크롤링 결과 출력"""
        if article_data:
            print("\n=== 기사 정보 ===")
            print(f"제목: {article_data[1]}")
            print(f"언론사: {article_data[2]}")
            print(f"기자: {article_data[3]}")
            print(f"날짜: {article_data[4]}")
            print(f"내용: {article_data[5][:100]}...")  # 내용은 일부만 출력

        if comment_data:
            print(f"\n=== 댓글 정보 ({len(comment_data)}개) ===")
            for i, (nickname, datetime, content, recomm, unrecomm) in enumerate(comment_data[:3], 1):
                print(f"\n댓글 {i}")
                print(f"작성자: {nickname}")
                print(f"날짜: {datetime}")
                print(f"내용: {content}")
                print(f"추천/비추천: {recomm}/{unrecomm}")

            if len(comment_data) > 3:
                print(f"\n... 외 {len(comment_data) - 3}개의 댓글")

    def run(self):
        """프로그램 실행"""
        self._print_header()

        while True:
            choice = self._get_menu_choice()
            if choice is None:
                continue

            if choice == 1:
                article_data, comment_data = self._crawl_single_url()
                self._print_results(article_data, comment_data)

            elif choice == 2:
                results = self._crawl_by_keyword()
                for idx, (article_data, comment_data) in enumerate(results, 1):
                    print(f"\n\n=== {idx}번째 기사 결과 ===")
                    self._print_results(article_data, comment_data)

            else:
                print("""
                ----------------------------------------
                      프로그램을 종료합니다. 감사합니다.
                ----------------------------------------
                """)
                break

            print("\n계속하려면 Enter를 누르세요...")
            input()


if __name__ == '__main__':
    program = NaverNewsCrawlerProgram()
    program.run()