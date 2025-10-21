#!/usr/bin/env python3
"""
유사 맵 검색 스크립트
FAISS 인덱스에서 쿼리와 유사한 맵을 검색합니다.

Usage:
    python search_maps.py <query> <faiss_index_path> <db_path> [top_k]

Output (stdout):
    JSON: [
        {
            "map_id": 1,
            "map_name": "crossroad_01",
            "description": "...",
            "category": "junction",
            "difficulty": "medium",
            "tags": ["교차로", "신호등"],
            "similarity_score": 0.95
        },
        ...
    ]
"""

import sys
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# Load environment variables
load_dotenv()


def log_error(message):
    """stderr로 에러 로그 출력"""
    print(f"ERROR: {message}", file=sys.stderr)


def load_map_metadata(db_path, map_id):
    """
    SQLite DB에서 맵 메타데이터 로드

    Args:
        db_path: SQLite DB 파일 경로
        map_id: 맵 ID

    Returns:
        dict: 맵 정보
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description, tags, category, difficulty,
               is_embedded, embedded_at, embedding_model
        FROM maps
        WHERE id = ?
    """, (map_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    map_data = dict(row)

    # Parse tags JSON string to array
    if map_data['tags']:
        try:
            map_data['tags'] = json.loads(map_data['tags'])
        except json.JSONDecodeError:
            # If not valid JSON, split by comma
            map_data['tags'] = [t.strip() for t in map_data['tags'].split(',')]
    else:
        map_data['tags'] = []

    return map_data


def search_similar_maps(query, faiss_index_path, db_path, top_k=5):
    """
    쿼리와 유사한 맵 검색

    Args:
        query: 검색 쿼리 문자열
        faiss_index_path: FAISS 인덱스 경로
        db_path: SQLite DB 경로
        top_k: 반환할 상위 맵 개수

    Returns:
        list: 검색 결과 리스트
    """
    faiss_path = Path(faiss_index_path)

    if not faiss_path.exists():
        raise FileNotFoundError(
            f"FAISS index not found at {faiss_index_path}. "
            "Please run build_all_embeddings.py first."
        )

    # OpenAI Embeddings 초기화
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

    # FAISS 인덱스 로드
    log_error(f"Loading FAISS index from {faiss_index_path}")
    vector_store = FAISS.load_local(
        faiss_index_path,
        embeddings,
        allow_dangerous_deserialization=True
    )

    # 유사도 검색
    log_error(f"Searching for: '{query}'")
    results = vector_store.similarity_search_with_score(query, k=top_k)

    # 결과 변환
    output = []
    for doc, distance in results:
        map_id = doc.metadata.get('map_id')

        if not map_id:
            log_error(f"Warning: Document missing map_id metadata")
            continue

        # DB에서 최신 메타데이터 로드
        map_data = load_map_metadata(db_path, map_id)

        if not map_data:
            log_error(f"Warning: Map not found in DB: id={map_id}")
            continue

        # Similarity score 계산 (FAISS는 L2 distance를 반환)
        # Lower distance = higher similarity
        # Normalize to 0-1 range (approximate)
        # Convert to native Python float for JSON serialization
        distance_float = float(distance)
        similarity_score = 1.0 / (1.0 + distance_float)

        output.append({
            'mapId': map_data['id'],
            'mapName': map_data['name'],
            'description': map_data['description'],
            'category': map_data['category'],
            'difficulty': map_data['difficulty'],
            'tags': map_data['tags'],
            'similarityScore': round(similarity_score, 4),
            'distance': round(distance_float, 4),
            'isEmbedded': bool(map_data['is_embedded'])
        })

    return output


def main():
    if len(sys.argv) < 4:
        log_error("Usage: python search_maps.py <query> <faiss_index_path> <db_path> [top_k]")
        sys.exit(1)

    try:
        query = sys.argv[1]
        faiss_index_path = sys.argv[2]
        db_path = sys.argv[3]
        top_k = int(sys.argv[4]) if len(sys.argv) > 4 else 5

        results = search_similar_maps(query, faiss_index_path, db_path, top_k)

        # stdout으로 JSON 배열 출력
        print(json.dumps(results, ensure_ascii=False, indent=2))

    except Exception as e:
        log_error(f"Failed to search maps: {e}")
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
