import sqlite3
import csv
import os

class FromDBToCSV:
    def __init__(self, db_name: str):
        """
        데이터 베이스 파일로부터 CSV 파일로 변환하는 클래스 초기화
        Args:
            db_name: SQLite 데이터 베이스 파일 이름!! ex. naver_news.db
        """
        self.db_name = db_name

    def export_table_to_csv(self, table_name: str, csv_file: str):
        """
        지정한 테이블의 데이터를 CSV 파일로 내보내는 메서드
        Args:
            table_name: CSV로 내보낼 데이터 베이스 테이블 이름
            csv_file: 결과 CSV 파일 경로
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                # 컬럼 헤더 추출
                headers = [description[0] for description in cursor.description]

            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(headers)
                writer.writerows(rows)

            print(f"{table_name} 테이블의 데이터가 '{csv_file}' 파일로 저장되었습니다.")
        except Exception as e:
            print(f"{table_name} 테이블을 CSV로 내보내는 중 오류 발생: {e}")

    def export_articles(self, csv_file: str = "articles.csv"):
        """
        articles 테이블의 데이터를 CSV 파일로 내보내는 메서드
        Args:
            csv_file: 저장할 CSV 파일 이름 = 기본값: articles.csv
        """
        self.export_table_to_csv("articles", csv_file)

    def export_comments(self, csv_file: str = "comments.csv"):
        """
        comments 테이블의 데이터를 CSV 파일로 내보내는 메서드
        Args:
            csv_file: 저장할 CSV 파일 이름 = 기본값: comments.csv
        """
        self.export_table_to_csv("comments", csv_file)

# 사용 예시
if __name__ == "__main__":
    path = input("데이터 베이스 파일(.db) 이름: ") # naver_db.db
    converter = FromDBToCSV(path)
    name = base_name = os.path.splitext(path)[0] # naver_db

    converter.export_articles(f"{name}_articles_export.csv")
    converter.export_comments(f"{name}_comments_export.csv")
