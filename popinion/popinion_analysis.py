import json
import sqlite3
import os
from collections import defaultdict
from datetime import datetime

import openai
import pandas as pd
from openai import OpenAI
from tqdm import tqdm


def get_openai_key(path):
    """API 키 불러오기"""
    with open(path, 'r', encoding='utf-8') as rr:
        return rr.read().strip()


def get_now():
    """현재 시간 포맷"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def create_log_file():
    """로그 파일을 생성하고 기본 정보 작성"""
    os.makedirs("open_ai_logs", exist_ok=True)  # 로그 폴더 생성
    log_filename = f"open_ai_logs/log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    with open(log_filename, 'w', encoding='utf-8') as log_file:
        log_file.write(f"{get_now()} - 분석 시작\n")

    return log_filename


def append_log(log_filename, log_text):
    """실시간 로그 저장 (파일에 추가 기록)"""
    print(log_text)  # 터미널에도 출력
    with open(log_filename, 'a', encoding='utf-8') as log_file:
        log_file.write(f"{get_now()} - {log_text}\n")


def extract_opinion_with_chatgpt(comments, log_filename):
    """ChatGPT API를 이용하여 댓글에서 여론을 추출하고 강도를 평가"""

    system_prompt = """
    당신은 뉴스 댓글을 분석하여 주요 여론을 분류하는 역할을 수행해야 한다. 
    주어진 댓글을 보고 포함된 여론을 추출하고, 각 여론의 강도를 0~5의 점수로 평가해야 한다.
    여론은 크게 세가지 

    - 주어진 대상에 대한 평가가 있을시, 이를 대상의 이름과 같이 여론에 반드시 추가해야 한다.
    - 여론의 분류는 최대 5개까지만 가능하며, 가능한 한 기존과 일관된 명칭을 사용해야 한다.
    - 여론 강도가 0이면 거의 의미 없는 의견이며, 5이면 매우 강한 여론이다.

    **출력 형식 (JSON)**
    {"opinion": [{"type": "여론 유형", "strength": 점수}, ...]}
    """

    results = []

    try:
        client = OpenAI(api_key=openai.api_key)
    except Exception as e:
        append_log(log_filename, f"❌ OpenAI Client 생성 실패: {str(e)}")
        return results

    append_log(log_filename, "✅ GPT-4 분석 시작...")

    for idx, comment in enumerate(tqdm(comments, desc="ChatGPT 여론 분석 중")):
        if not comment.strip():
            append_log(log_filename, f"[{idx + 1}] 빈 댓글 스킵됨.")
            results.append(None)
            continue

        prompt = f"뉴스 댓글: \"{comment}\"\n\n이 댓글에 포함된 여론을 분석하여 JSON 형식으로 제공해라."

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            response_dict = response.model_dump()
            response_text = response_dict["choices"][0]["message"]["content"]
            parsed_response = json.loads(response_text)

            if "opinion" in parsed_response:
                results.append(parsed_response["opinion"])
                append_log(log_filename,
                           f"[{idx + 1}] 댓글 분석 완료 ✅\n{comment}\n결과: {json.dumps(parsed_response, ensure_ascii=False, indent=2)}\n")
            else:
                results.append(None)
                append_log(log_filename, f"[{idx + 1}] GPT-4 분석 실패 ❌\n{comment}\n결과: 없음\n")

        except Exception as e:
            append_log(log_filename, f"[{idx + 1}] API 요청 실패 ❌: {str(e)}")
            results.append(None)

    return results


def load_comments_from_db(db_paths, log_filename):
    """SQLite 데이터베이스에서 댓글 데이터를 로드"""
    all_comments = []
    for db_path in db_paths:
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT nickname, content FROM comments WHERE nickname IS NOT NULL AND content IS NOT NULL"
            df = pd.read_sql_query(query, conn)
            df = df[df['content'].str.strip().astype(bool)]
            df = df[df['nickname'].str.strip().astype(bool)]
            conn.close()
            all_comments.append(df)
        except sqlite3.Error as e:
            append_log(log_filename, f"데이터베이스 오류 ({db_path}): {str(e)}")
            continue

    if not all_comments:
        raise ValueError("처리할 수 있는 댓글 데이터가 없습니다.")

    final_df = pd.concat(all_comments, ignore_index=True)
    append_log(log_filename, f"총 {len(final_df)}개의 유효한 댓글을 로드했습니다.")
    return final_df


def main():

    try:
        db_paths = [
            "../databases/윤석열_50_0_250219.db",  # 키워드_기사개수_정렬방법_기사날짜.db
        ]

        log_filename = create_log_file()  # 로그 파일 생성

        append_log(log_filename, "댓글 데이터 로딩 중...")
        comments_df = load_comments_from_db(db_paths, log_filename)

        if len(comments_df) > MAX_COMMENT_NUM:
            comments_df = comments_df[:MAX_COMMENT_NUM]
            append_log(log_filename, f"최대 댓글 수를 넘어 {MAX_COMMENT_NUM}개로 조정하였습니다.")

        append_log(log_filename, "ChatGPT를 이용한 여론 분석 시작...")
        comments_df['opinion_scores'] = extract_opinion_with_chatgpt(comments_df['content'].tolist(), log_filename)

        append_log(log_filename, "\n✅ 분석 완료. 최종 여론 결과 정리 중...")

        total_users = len(comments_df)
        append_log(log_filename, f"총 사용자 수: {total_users}")

        append_log(log_filename, "📊 주요 여론 분석 결과:")
        for idx, row in comments_df.iterrows():
            if row['opinion_scores']:
                append_log(log_filename,
                           f"[{idx + 1}] {row['nickname']}: {json.dumps(row['opinion_scores'], ensure_ascii=False)}")

        append_log(log_filename, "\n✅ 분석 및 로그 저장 완료!")

    except Exception as e:
        append_log(log_filename, f"프로그램 실행 중 오류 발생: {str(e)}")


if __name__ == "__main__":
    MAX_COMMENT_NUM = 10
    OPENAI_API_KEY_PATH = r"C:\Users\gaeba\Downloads\POA_OPENAI_KEY.txt"
    openai.api_key = get_openai_key(OPENAI_API_KEY_PATH)
    main()
