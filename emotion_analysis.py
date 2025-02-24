import sqlite3
import pandas as pd
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch
from collections import defaultdict
from tqdm import tqdm
import os


def load_comments_from_db(db_paths):
    """SQLite 데이터베이스에서 댓글 데이터를 로드"""
    all_comments = []
    for db_path in db_paths:
        try:
            conn = sqlite3.connect('databases/'+db_path)
            query = "SELECT nickname, content FROM comments WHERE nickname IS NOT NULL AND content IS NOT NULL"
            df = pd.read_sql_query(query, conn)
            # 빈 문자열이나 공백만 있는 경우도 제거
            df = df[df['content'].str.strip().astype(bool)]
            df = df[df['nickname'].str.strip().astype(bool)]
            conn.close()
            all_comments.append(df)
        except sqlite3.Error as e:
            print(f"데이터베이스 오류 ({db_path}): {str(e)}")
            continue

    if not all_comments:
        raise ValueError("처리할 수 있는 댓글 데이터가 없습니다.")

    final_df = pd.concat(all_comments, ignore_index=True)
    print(f"총 {len(final_df)}개의 유효한 댓글을 로드했습니다.")
    return final_df


def analyze_sentiment(comments):
    """Hugging Face 모델을 사용하여 감성 분석 수행"""
    model_name = "snunlp/KR-FinBert-SC"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)

    results = []
    batch_size = 16
    max_length = 512  # 최대 토큰 길이 설정

    # null이나 빈 문자열이 아닌 댓글만 처리
    valid_comments = [comment for comment in comments if pd.notna(comment) and str(comment).strip()]

    for i in range(0, len(valid_comments), batch_size):
        batch = valid_comments[i:i + batch_size]
        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=max_length,  # 최대 길이 지정
            return_tensors="pt"
        )
        with torch.no_grad():
            outputs = model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)[:, 1].tolist()
        results.extend(scores)

    # 원본 댓글 리스트 길이만큼 결과 리스트 생성
    final_results = []
    valid_idx = 0
    for comment in comments:
        if pd.notna(comment) and str(comment).strip():
            final_results.append(results[valid_idx])
            valid_idx += 1
        else:
            final_results.append(None)

    return final_results

def aggregate_sentiment_by_user(comments_df):
    """아이디별 감성 점수를 집계하여 최종 긍정/부정 판단"""
    if comments_df.empty:
        raise ValueError("분석할 댓글이 없습니다.")

    user_sentiments = defaultdict(list)
    for _, row in comments_df.iterrows():
        if pd.notna(row['sentiment_score']):  # NaN 값 체크
            user_sentiments[row['nickname']].append(row['sentiment_score'])

    final_sentiments = {
        user: sum(scores) / len(scores) > 0.5
        for user, scores in user_sentiments.items()
        if scores  # 빈 리스트 제외
    }
    return final_sentiments


def main():
    try:
        db_paths = [
            "윤석열_50_0_250223.db", # 키워드_기사개수_정렬방법_기사날짜.db
        ]

        print("댓글 데이터 로딩 중...")
        comments_df = load_comments_from_db(db_paths)
        print(f"총 {len(comments_df)}개의 댓글을 로드했습니다.")

        comments_df['sentiment_score'] = analyze_sentiment(comments_df['content'].tolist())
        final_sentiments = aggregate_sentiment_by_user(comments_df)

        positive_users = sum(final_sentiments.values())
        total_users = len(final_sentiments)

        print("\n=== 분석 결과 ===")
        print(f"총 사용자 수: {total_users}")
        print(f"긍정 비율: {positive_users / total_users * 100:.2f}%")
        print(f"부정 비율: {(1 - positive_users / total_users) * 100:.2f}%")

        print("\n=== 샘플 분석 ===")
        sample_users = list(final_sentiments.keys())[:5]
        for user in sample_users:
            user_comments = comments_df[comments_df['nickname'] == user]['content'].tolist()
            sentiment = "긍정" if final_sentiments[user] else "부정"
            print(f"\n[아이디: {user}] → {sentiment}")
            print("예시 댓글:", user_comments[:3])

    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    main()