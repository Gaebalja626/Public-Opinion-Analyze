from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType
import numpy as np
from typing import List, Tuple


# cnn = connections.connect(host='127.0.0.1', port='19530')
# collection = Collection(name='Data_Embeddings')
# collection.drop()


class MilvusManager:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 19530
        self.collection_name = "Data_Embeddings"

    def connect(self):
        """Milvus 서버에 연결"""
        try:
            connections.connect(host=self.host, port=self.port)
            print("Milvus 서버 연결 성공")
        except Exception as e:
            raise Exception(f"Milvus 연결 실패: {str(e)}")

    def create_collection(self):
        """컬렉션 생성"""
        try:
            # 필드 정의
            fields = [
                FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
                FieldSchema(name="comment_vector", dtype=DataType.FLOAT_VECTOR, dim=1024),
                FieldSchema(name="comment_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=2)
            ]
            schema = CollectionSchema(fields=fields, description="Data embeddings")

            # 컬렉션 생성
            collection = Collection(name=self.collection_name, schema=schema)
            print(f"컬렉션 '{self.collection_name}' 생성 완료")
        except Exception as e:
            raise Exception(f"컬렉션 생성 실패: {str(e)}")

    def save_embeddings(self, embeddings_data: List[Tuple[str, np.ndarray]]):
        """
        임베딩 데이터를 Milvus에 저장
        Args:
            embeddings_data: [(user_id, embedding), ...] 형태의 리스트
        """
        try:
            collection = Collection(self.collection_name)

            # 데이터 준비
            user_ids = [item[0] for item in embeddings_data]
            vectors = [item[1].tolist() for item in embeddings_data]

            # reduced vectors는 임시로 빈 벡터로 설정
            empty_reduced = [[0.0, 0.0]] * len(user_ids)

            # 데이터 삽입
            entities = [
                user_ids,
                vectors,
                empty_reduced
            ]

            collection.insert(entities)
            print(f"{len(user_ids)}개의 임베딩 데이터 저장 완료")

            # 변경사항 적용
            collection.flush()

        except Exception as e:
            raise Exception(f"데이터 저장 실패: {str(e)}")
        finally:
            connections.disconnect("default")


def save_to_milvus(embeddings_result: List[Tuple[str, np.ndarray]]):
    """
    임베딩 결과를 Milvus에 저장하는 메인 함수
    Args:
        embeddings_result: embedding.py에서 반환된 결과
    """
    try:
        manager = MilvusManager()
        manager.connect()
        manager.create_collection()
        manager.save_embeddings(embeddings_result)
        print("Milvus 저장 완료")
    except Exception as e:
        print(f"Milvus 저장 실패: {str(e)}")


# 사용 예시:
if __name__ == "__main__":
    from data_analysis.embedding import Embedder

    embedder = Embedder("test.db")
    result = embedder.embedding()
    save_to_milvus(result)