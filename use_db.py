# use_db.py

import sqlite3
import pandas as pd
import os

DB_FILENAME = '뉴스 기사와 댓글.db'


# 내부 함수: 데이터베이스 초기화
def _initialize_db():
    """데이터베이스 및 테이블 자동 초기화 (내부 호출 전용)"""
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    # article 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS article (
        article_id INTEGER PRIMARY KEY AUTOINCREMENT,
        제목 TEXT,
        작성시점 TEXT,
        기자이름 TEXT,
        본문 TEXT,
        언론사 TEXT,
        URL TEXT
    )
    ''')

    # comment 테이블
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS comment (
        comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        작성자 TEXT,
        시간 TEXT,
        내용 TEXT,
        article_id INTEGER,
        FOREIGN KEY(article_id) REFERENCES article(article_id)
    )
    ''')

    conn.commit()
    conn.close()
    print("[DB] 데이터베이스 및 테이블 초기화 완료")


# 기사 및 댓글 데이터 삽입
def insert_article_and_comments(article_df, comment_df):
    """기사 및 댓글 데이터를 데이터베이스에 삽입"""

    # [STEP 1] 데이터베이스 초기화 (최초 1회 자동)
    if not os.path.exists(DB_FILENAME):
        print("[DB] 데이터베이스 파일이 없습니다. 자동으로 생성합니다.")
        _initialize_db()

    # [STEP 2] 데이터베이스 연결
    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    # [STEP 3] 기사(article) 삽입
    article_df.to_sql('article', conn, if_exists='append', index=False)

    # 방금 삽입된 article_id 가져오기
    cursor.execute('SELECT last_insert_rowid()')
    article_id = cursor.fetchone()[0]
    print(f"[DB] 삽입된 기사 article_id: {article_id}")

    # [STEP 4] 댓글(comment) 삽입
    comment_df['article_id'] = article_id
    comment_df.to_sql('comment', conn, if_exists='append', index=False)

    # [STEP 5] 확인 및 종료
    conn.commit()
    conn.close()
    print(f"[DB] article_id={article_id}에 대한 댓글 삽입 완료")
