from typing import Optional, Tuple, List
import logging
from datetime import datetime
import os

from crawler.news_crawler import NaverNewsCrawler
from crawler.url_crawler import NaverNewsURLCrawler
from db.news_db_manager import NewsDBManager


class NaverNewsCrawlerProgram:
    def __init__(self):
        """네이버 뉴스 크롤러 프로그램 초기화"""
        self._setup_logging()
        self.db_manager_list = self._load_existing_databases()

    def _load_existing_databases(self) -> List[Tuple[str, NewsDBManager]]:
        """
        기존 데이터베이스 파일들을 로드
        Returns:
            List of tuples containing (db_name, db_manager)
        """
        db_list = []
        db_directory = "databases"  # 데이터베이스 파일들이 저장된 디렉토리

        # 디렉토리가 없으면 생성
        if not os.path.exists(db_directory):
            os.makedirs(db_directory)

        # .db 파일들을 찾아서 매니저 생성
        for filename in os.listdir(db_directory):
            if filename.endswith('.db'):
                db_name = filename[:-3]  # .db 확장자 제거
                db_manager = NewsDBManager(os.path.join(db_directory, db_name))
                db_list.append((db_name, db_manager))

        return db_list

    def _setup_logging(self):
        """로깅 설정"""
        log_directory = "logs"
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

        logging.basicConfig(
            filename=os.path.join(log_directory, f'crawler_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            encoding='utf-8'
        )

    def _validate_date_format(self, date_str: str) -> bool:
        """날짜 형식이 올바른지 검증"""
        try:
            datetime.strptime(date_str, '%Y.%m.%d')
            return True
        except ValueError:
            return False

    def _print_header(self):
        """프로그램 헤더 출력
        ----------------------------------------
                네이버 뉴스 크롤러 v1.0
        ----------------------------------------
        """
        print("""
        ----------------------------------------
                네이버 뉴스 크롤러 v1.0
        ----------------------------------------
        """)

    def _get_menu_choice(self) -> Optional[int]:
        """
        메뉴 선택 받기

        크롤링 방법을 선택해주세요:

        1) 네이버 뉴스 URL로 크롤링
        2) 키워드 검색으로 크롤링
        3) 종료

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
        while True:
            try:
                sort_by = int(input("정렬 기준을 선택해주세요 (0-관련도 순, 1-최신 순, 2-오래된 순): "))
                if sort_by not in [0,1,2]:
                    print("올바른 숫자를 입력해주세요.")
                    continue
                break
            except ValueError:
                print("올바른 숫자를 입력해주세요.")
        while True:
            try:
                date_option = input("전체 기간에 대해 검색하시겠습니까? (y/n): ")
                if date_option not in ['y','n']:
                    continue
                break
            except ValueError:
                print("올바른 문자를 입력해주세요.")
        while True:
            if date_option == 'n':
                print("\n날짜 형식은 YYYY.MM.DD 입니다. (예: 2024.02.25)")
                while True:
                    start_date = input("시작 날짜를 입력해주세요: ")
                    if not self._validate_date_format(start_date):
                        print("올바른 날짜 형식이 아닙니다. 다시 입력해주세요.")
                        continue

                    while True:
                        end_date = input("종료 날짜를 입력해주세요: ")
                        if not self._validate_date_format(end_date):
                            print("올바른 날짜 형식이 아닙니다. 다시 입력해주세요.")
                            continue

                        start = datetime.strptime(start_date, '%Y.%m.%d')
                        end = datetime.strptime(end_date, '%Y.%m.%d')

                        if end < start:
                            print("종료 날짜는 시작 날짜보다 늦어야 합니다.")
                            continue

                        date_range = (start_date, end_date)
                        break
                    break
                break
            elif date_option == 'y':
                date_range = '',''  # 전체 기간 검색
                break


        logging.info(f"키워드 검색 크롤링 시작 - 키워드: {keyword}, 요청 개수: {number}, 정렬 기준: {sort_by}, 전체 기간 검색: {date_option}")

        results = []
        try:
            url_crawler = NaverNewsURLCrawler(keyword, number, sort_by, date_range)
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

    def _select_database(self) -> Optional[NewsDBManager]:
        """
        저장할 데이터베이스 선택
        Returns:
            선택된 NewsDBManager 인스턴스
        """
        print("\n=== DB 저장을 시작합니다 ===")

        # 현재 사용 가능한 DB 목록 출력
        if self.db_manager_list:
            print("\n현재 사용 가능한 DB 목록:")
            for idx, (db_name, _) in enumerate(self.db_manager_list, 1):
                print(f"{idx}) {db_name}")
        else:
            print("\n사용 가능한 DB가 없습니다.")

        while True:
            try:
                choice = input("\n새로운 DB를 만드시려면 0, 기존 DB에 저장하시려면 해당 번호를 입력해주세요: ")
                db_choice = int(choice)

                if db_choice == 0:
                    # 새 DB 생성
                    while True:
                        db_name = input("새로 생성할 DB의 이름을 입력해주세요: ")
                        db_path = os.path.join("databases", db_name)

                        if os.path.exists(f"{db_path}.db"):
                            print("이미 존재하는 DB 이름입니다. 다른 이름을 입력해주세요.")
                            continue

                        db_manager = NewsDBManager(db_path)
                        self.db_manager_list.append((db_name, db_manager))
                        return db_manager

                elif 1 <= db_choice <= len(self.db_manager_list):
                    # 기존 DB 선택
                    return self.db_manager_list[db_choice - 1][1]
                else:
                    print("올바른 번호를 입력해주세요.")

            except ValueError:
                print("숫자를 입력해주세요.")

    def _save_crawling_results(self, article_data, comment_data) -> bool:
        """
        크롤링 결과를 데이터베이스에 저장
        Args:
            article_data: 단일 기사 데이터 또는 기사 데이터 리스트
            comment_data: 단일 댓글 데이터 또는 댓글 데이터 리스트
        Returns:
            저장 성공 여부
        """
        try:
            db_manager = self._select_database()
            if db_manager is None:
                return False

            # 단일 기사인 경우 리스트로 변환
            if isinstance(article_data, list) and not isinstance(article_data[0], list):
                article_data = [article_data]
                comment_data = [comment_data]

            success = True
            for idx, (article, comments) in enumerate(zip(article_data, comment_data)):
                if not article:  # 빈 기사 데이터 건너뛰기
                    continue

                try:
                    if not db_manager.save_article(article):
                        logging.error(f"기사 저장 실패: {article[0]}")
                        success = False
                        continue

                    if comments:
                        if not db_manager.save_comments(article[0], comments):
                            logging.error(f"댓글 저장 실패: {article[0]}")
                            success = False

                    print(f"\n{idx + 1}번째 기사 저장 완료")

                except Exception as e:
                    logging.error(f"데이터 저장 중 오류 발생: {str(e)}")
                    success = False
                    continue

            return success

        except Exception as e:
            logging.error(f"데이터 저장 중 오류 발생: {str(e)}")
            print(f"데이터 저장 중 오류가 발생했습니다: {str(e)}")
            return False
    def _print_preview(self, article_data: list, comment_data: list):
        """크롤링 결과 출력 및 저장"""
        if article_data:
            print("\n=== 기사 정보 ===")
            print(f"제목: {article_data[1]}")
            print(f"언론사: {article_data[2]}")
            print(f"기자: {article_data[3]}")
            print(f"날짜: {article_data[4]}")
            print(f"내용: {article_data[5][:100]}...")

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

        # # 저장 프로세스 실행
        # if self._save_crawling_results(article_data, comment_data):
        #     print("\n데이터베이스 저장이 완료되었습니다.")
        # else:
        #     print("\n데이터베이스 저장 중 오류가 발생했습니다.")


    def run(self):
        """프로그램 실행"""
        self._print_header()

        while True:
            choice = self._get_menu_choice()
            if choice is None:
                continue

            if choice == 1:  # 단일 URL
                article_data, comment_data = self._crawl_single_url()
                if article_data:
                    self._print_preview(article_data, comment_data)
                    if self._save_crawling_results(article_data, comment_data):
                        print("\n데이터베이스 저장이 완료되었습니다.")
                    else:
                        print("\n데이터베이스 저장 중 오류가 발생했습니다.")

            elif choice == 2:  # 키워드 검색
                results = self._crawl_by_keyword()
                if results:
                    articles, comments = zip(*results)
                    for idx, (article_data, comment_data) in enumerate(results, 1):
                        print(f"\n\n=== {idx}번째 기사 결과 ===")
                        self._print_preview(article_data, comment_data)

                    if self._save_crawling_results(articles, comments):
                        print("\n모든 데이터베이스 저장이 완료되었습니다.")
                    else:
                        print("\n일부 데이터 저장 중 오류가 발생했습니다.")

            else:
                print("""
                ----------------------------------------
                      프로그램을 종료합니다. 감사합니다.
                ----------------------------------------
                """)
                break

            print("\n계속하려면 Enter를 누르세요...")
            _ = input()
if __name__ == '__main__':
    program = NaverNewsCrawlerProgram()
    program.run()