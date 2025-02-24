import sqlite3
import re
from typing import List, Tuple
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self, db_name: str):
        """
        Args:
            db_path: SQLite DB 파일 경로
        """
        self.model = SentenceTransformer("upskyy/bge-m3-korean")
        self.db_path = r"C:\Users\USER\PycharmProjects\Public-Opinion-Analyze\databases\\"+db_name
        self.user_id: List[str] = []
        self.result: List[Tuple[str, np.ndarray]] = []

    def load_data(self) -> List[str]:
        """
        Returns:
            전처리할 댓글 내용 리스트
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT nickname, content FROM comments")
            data = cursor.fetchall()
            print("데이터 긁어오기 성공")

            # 사용자별로 댓글 모으기
            user_comments = defaultdict(list)
            for user_id, comment in data:
                user_comments[str(user_id)].append(str(comment))
            print("데이터 정리 성공")

            # 사용자별 댓글을 하나의 문자열로 병합
            self.user_id = list(user_comments.keys())
            comment_content = [' '.join(comments) for comments in user_comments.values()]
            print("데이터 병합 성공")

            return comment_content

        except sqlite3.Error as e:
            raise Exception(f"데이터베이스 로딩 중 오류 발생: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def preprocessing(self, comment_content: List[str]) -> List[str]:
        """
        Args:
            comment_content: 전처리할 댓글 내용 리스트
        Returns:
            전처리된 댓글 내용 리스트
        """
        preprocessed = []
        for content in comment_content:

            # 3. 특수문자 제거 (단, 한글, 영문, 숫자, 기본 문장부호는 유지)
            content = re.sub(r'[^\w\s가-힣.,!?]', ' ', content)

            # 4. 이모티콘 제거
            content = re.sub(r'[\U00010000-\U0010ffff]', '', content)

            # 5. 연속된 공백 제거
            content = re.sub(r'\s+', ' ', content)

            # 6. 앞뒤 공백 제거
            content = content.strip()

            # 7. 빈 문자열이 아닌 경우만 추가
            if content:
                preprocessed.append(content)
        print("데이터 전처리 성공")
        return preprocessed

    def embedding(self) -> List[Tuple[str, np.ndarray]]:
        """
        Returns:
            [(user_id, embedding), ...] 형태의 결과 리스트
        """
        try:
            comment_content = self.load_data()
            preprocessed_content = self.preprocessing(comment_content)

            if not preprocessed_content:
                raise ValueError("전처리된 댓글이 없습니다.")
            print("데이터 임베딩 시작")
            embeddings = self.model.encode(preprocessed_content)
            self.result = list(zip(self.user_id[:len(preprocessed_content)], embeddings))

            return self.result

        except Exception as e:
            raise Exception(f"임베딩 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    try:
        embedder = Embedder("test.db")
        result = embedder.embedding()
        print(f"임베딩된 댓글 수: {len(result)}")
        print(result)
    except Exception as e:
        print(f"오류 발생: {str(e)}")