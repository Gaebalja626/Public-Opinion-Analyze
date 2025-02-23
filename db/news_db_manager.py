import sqlite3
from typing import List, Tuple, Dict, Optional
from datetime import datetime

class NewsDBManager:
    def __init__(self, db_name: str):
        """
        뉴스 데이터베이스 관리자 초기화
        Args:
            db_name: 데이터베이스 파일 이름
        """
        self.db_name = db_name+'.db'
        self._create_tables()

    def _create_tables(self):
        """데이터베이스 테이블 생성"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # 기사 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    article_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    journal_id TEXT NOT NULL,
                    reporter_id TEXT,
                    published_date TEXT NOT NULL,
                    modified_date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 댓글 테이블 생성
            # TODO comment_id
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    article_id TEXT NOT NULL,
                    nickname TEXT,
                    datetime TEXT,
                    content TEXT,
                    recommends INTEGER,
                    unrecommends INTEGER,
                    FOREIGN KEY (article_id) REFERENCES articles (article_id)
                )
            """)

            conn.commit()

    def save_article(self, article_data: List) -> bool:
        """
        기사 데이터 저장
        Args:
            article_data: [article_id, title, journal, reporter, datetime, content]
        Returns:
            저장 성공 여부
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO articles 
                    (article_id, title, journal_id, reporter_id, published_date, modified_date, content)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, article_data)
                conn.commit()
                return True
        except Exception as e:
            print(f"기사 저장 중 오류 발생: {str(e)}")
            return False

    def save_comments(self, article_id: str, comment_data: List[Tuple]) -> bool:
        """
        댓글 데이터 저장
        Args:
            article_id: 기사 ID
            comment_data: [(nickname, datetime, content, recommends, unrecommends), ...]
        Returns:
            저장 성공 여부
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                for comment in comment_data:
                    try:
                        recommends = int(comment[3].replace(',', ''))
                        unrecommends = int(comment[4].replace(',', ''))
                    except:
                        recommends, unrecommends = None, None

                    cursor.execute("""
                        INSERT INTO comments 
                        (article_id, nickname, datetime, content, recommends, unrecommends)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (article_id, *comment[:3], recommends, unrecommends))
                conn.commit()
                return True
        except Exception as e:
            print(f"댓글 저장 중 오류 발생: {str(e)}")
            return False

    def get_article_count(self) -> int:
        """저장된 기사 수 조회"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM articles")
            return cursor.fetchone()[0]

    def get_comment_count(self) -> int:
        """저장된 댓글 수 조회"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM comments")
            return cursor.fetchone()[0]

    # db 내 검색할 때 메인되는 메소드입니다.
    # 다른 요소들로 검색을 하더라도 article_id로 반환되도록 함수 짜주시고
    # 반환된 article_id를 이 함수에 넣어 최종적인 데이터들을 가져오는 로직이 좋지 않을까 합니다.
    def get_article_with_comments(self, article_id: str) -> Optional[Dict]:
        """
        기사와 해당 기사의 모든 댓글 조회
        Args:
            article_id: 조회할 기사 ID
        Returns:
            기사 정보와 댓글 목록을 포함하는 딕셔너리 또는 None
        """
        with sqlite3.connect(self.db_name) as conn:
            conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하도록 설정
            cursor = conn.cursor()

            # 기사 정보 조회
            cursor.execute("""
                SELECT * FROM articles WHERE article_id = ?
            """, (article_id,))
            article = cursor.fetchone()

            if not article:
                return None

            # 댓글 목록 조회
            cursor.execute("""
                SELECT * FROM comments 
                WHERE article_id = ?
                ORDER BY datetime DESC
            """, (article_id,))
            comments = cursor.fetchall()

            # 결과 딕셔너리 구성
            result = {
                'article': dict(article),
                'comments': [dict(comment) for comment in comments],
                'comment_count': len(comments)
            }

            return result

    def search_article_ids(self, keyword: str) -> List[int]:
        """
        기사 검색 (제목 기준) 후 article_id 반환
        Args:
            keyword: 검색할 키워드
        Returns:
            검색된 기사의 article_id 목록
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT article_id
                FROM articles
                WHERE title LIKE ?
            """, (f'%{keyword}%',))

            results = cursor.fetchall()

            return [row[0] for row in results]

