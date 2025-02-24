from pymilvus import connections, db, FieldSchema, CollectionSchema, DataType, Collection
import atexit

from pymilvus.orm import utility

# 설정값 정의
MILVUS_CONFIG = {
    "host": "127.0.0.1",
    "port": 19530,
    "database": "test",
    "vector_dims": {
        "article": 768,
        "comment": 512,
        "user": 512,
        "journal": 512,
        "journalist": 512,
        "reduced": 2
    }
}

index_params = {"metric_type": "L2", "index_type": "IVF_FLAT", "params": {"nlist": 1024}}


def create_collection(name: str, schema: CollectionSchema) -> Collection:
    """컬렉션 생성 함수"""
    if utility.has_collection(name):
        print(f"컬렉션 {name}이 이미 존재합니다")
        return Collection(name)
    return Collection(name=name, schema=schema)


try:
    # Milvus 연결
    connections.connect(
        host=MILVUS_CONFIG["host"],
        port=MILVUS_CONFIG["port"]
    )
    database = db.create_database(MILVUS_CONFIG["database"])

    # Article 컬렉션
    article_fields = [
        FieldSchema(name="article_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="article_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["article"]),
        FieldSchema(name="article_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["reduced"])
    ]
    article_schema = CollectionSchema(fields=article_fields, description="Article content embeddings")
    article_collection = create_collection("Article_Embeddings", article_schema)
    article_collection.create_index("article_vector",index_params)

    # Comment 컬렉션
    comment_fields = [
        FieldSchema(name="comment_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="comment_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["comment"]),
        FieldSchema(name="comment_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["reduced"])
    ]
    comment_schema = CollectionSchema(fields=comment_fields, description="Comment embeddings")
    comment_collection = create_collection("Comment_Embeddings", comment_schema)
    comment_collection.create_index("comment_vector",index_params)

    # User 컬렉션
    user_fields = [
        FieldSchema(name="user_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="user_tendency_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["user"]),
        FieldSchema(name="user_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["reduced"])
    ]
    user_schema = CollectionSchema(fields=user_fields, description="User embeddings")
    user_collection = create_collection("User_Embeddings", user_schema)
    user_collection.create_index("user_tendency_vector",index_params)

    # Journal 컬렉션
    journal_fields = [
        FieldSchema(name="journal_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="journal_tendency_vector", dtype=DataType.FLOAT_VECTOR,
                    dim=MILVUS_CONFIG["vector_dims"]["journal"]),
        FieldSchema(name="journal_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["reduced"])
    ]
    journal_schema = CollectionSchema(fields=journal_fields, description="Journal embeddings")
    journal_collection = create_collection("Journal_Embeddings", journal_schema)
    journal_collection.create_index("journal_tendency_vector",index_params)

    # Journalist 컬렉션
    journalist_fields = [
        FieldSchema(name="journalist_id", dtype=DataType.VARCHAR, max_length=100, is_primary=True),
        FieldSchema(name="journalist_tendency_vector", dtype=DataType.FLOAT_VECTOR,
                    dim=MILVUS_CONFIG["vector_dims"]["journalist"]),
        FieldSchema(name="journalist_reduced_vector", dtype=DataType.FLOAT_VECTOR, dim=MILVUS_CONFIG["vector_dims"]["reduced"])
    ]
    journalist_schema = CollectionSchema(fields=journalist_fields, description="Journalist embeddings")
    journalist_collection = create_collection("Journalist_Embeddings", journalist_schema)
    journalist_collection.create_index("journalist_tendency_vector",index_params)

    # 컬렉션 로드
    for collection in [article_collection, comment_collection, user_collection, journal_collection,
                       journalist_collection]:
        collection.load()

    print("Milvus collections created successfully!")

except Exception as e:
    print(f"Error creating Milvus collections: {e}")


def cleanup():
    """연결 해제 함수"""
    connections.disconnect("default")


# 프로그램 종료 시 연결 해제
atexit.register(cleanup)
