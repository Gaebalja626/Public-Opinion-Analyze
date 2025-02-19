import sqlite3
from typing import List, Tuple
from datetime import datetime


class NewsDBManager:
    def __init__(self, db_name: str = "naver_news.db"):
        """
        뉴스 데이터베이스 관리자 초기화
        Args:
            db_name: 데이터베이스 파일 이름
        """
        self.db_name = db_name
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
                    journal TEXT NOT NULL,
                    reporter TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    content TEXT NOT NULL,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 댓글 테이블 생성
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    article_id TEXT NOT NULL,
                    nickname TEXT NOT NULL,
                    datetime TEXT NOT NULL,
                    content TEXT NOT NULL,
                    recommends INTEGER NOT NULL,
                    unrecommends INTEGER NOT NULL,
                    crawled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
                    (article_id, title, journal, reporter, published_date, content)
                    VALUES (?, ?, ?, ?, ?, ?)
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
                    recommends = int(comment[3].replace(',', ''))
                    unrecommends = int(comment[4].replace(',', ''))

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