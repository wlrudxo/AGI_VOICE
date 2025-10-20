#!/usr/bin/env python3
"""
단일 맵 임베딩 스크립트
SQLite DB에서 맵을 로드하고 OpenAI Embeddings를 생성하여 FAISS 인덱스에 저장합니다.

Usage:
    python embed_map.py <map_id> <faiss_index_path> <db_path>

Output (stdout):
    JSON: {"success": true, "map_id": 1, "embedded_at": "2025-01-20T12:00:00", "embedding_model": "text-embedding-3-small"}
"""

import sys
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

# Load environment variables
load_dotenv()


def log_error(message):
    """stderr로 에러 로그 출력"""
    print(f"ERROR: {message}", file=sys.stderr)


def load_map_from_db(db_path, map_id):
    """
    SQLite DB에서 맵 정보 로드

    Args:
        db_path: SQLite DB 파일 경로
        map_id: 맵 ID

    Returns:
        dict: 맵 정보 (id, name, description, ...)
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, description, tags, category, difficulty, node_xml, edge_xml
        FROM maps
        WHERE id = ?
    """, (map_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError(f"Map not found: id={map_id}")

    return dict(row)


def update_embedding_status(db_path, map_id, embedding_model):
    """
    DB에 임베딩 완료 상태 업데이트

    Args:
        db_path: SQLite DB 파일 경로
        map_id: 맵 ID
        embedding_model: 사용된 임베딩 모델명
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        UPDATE maps
        SET is_embedded = 1,
            embedded_at = ?,
            embedding_model = ?,
            updated_at = ?
        WHERE id = ?
    """, (now, embedding_model, now, map_id))

    conn.commit()
    conn.close()


def embed_map(map_id, faiss_index_path, db_path):
    """
    단일 맵 임베딩 생성 및 FAISS 인덱스 업데이트

    Args:
        map_id: 맵 ID
        faiss_index_path: FAISS 인덱스 저장 경로
        db_path: SQLite DB 경로

    Returns:
        dict: 결과 정보
    """
    # OpenAI Embeddings 초기화
    embedding_model_name = "text-embedding-3-small"
    embeddings = OpenAIEmbeddings(model=embedding_model_name)

    # DB에서 맵 로드
    map_data = load_map_from_db(db_path, map_id)

    # Document 생성 (description을 임베딩)
    doc = Document(
        page_content=map_data['description'],
        metadata={
            'map_id': map_data['id'],
            'map_name': map_data['name'],
            'category': map_data['category'],
            'difficulty': map_data['difficulty'],
            'tags': map_data['tags']  # JSON string
        }
    )

    # FAISS 인덱스 로드 또는 생성
    faiss_path = Path(faiss_index_path)
    faiss_index_file = faiss_path / "index.faiss"

    if faiss_index_file.exists():
        # 기존 인덱스 로드
        log_error(f"Loading existing FAISS index from {faiss_index_path}")
        vector_store = FAISS.load_local(
            faiss_index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        # 새 문서 추가
        vector_store.add_documents([doc])
    else:
        # 새 인덱스 생성
        log_error(f"Creating new FAISS index at {faiss_index_path}")
        faiss_path.mkdir(parents=True, exist_ok=True)
        vector_store = FAISS.from_documents([doc], embeddings)

    # 인덱스 저장
    vector_store.save_local(faiss_index_path)

    # DB 업데이트
    update_embedding_status(db_path, map_id, embedding_model_name)

    embedded_at = datetime.now(timezone.utc).isoformat()

    return {
        'success': True,
        'map_id': map_id,
        'map_name': map_data['name'],
        'embedded_at': embedded_at,
        'embedding_model': embedding_model_name
    }


def main():
    if len(sys.argv) != 4:
        log_error("Usage: python embed_map.py <map_id> <faiss_index_path> <db_path>")
        sys.exit(1)

    try:
        map_id = int(sys.argv[1])
        faiss_index_path = sys.argv[2]
        db_path = sys.argv[3]

        result = embed_map(map_id, faiss_index_path, db_path)

        # stdout으로 JSON 출력 (Rust에서 파싱)
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        log_error(f"Failed to embed map: {e}")
        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
