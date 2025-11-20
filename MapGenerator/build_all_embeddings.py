#!/usr/bin/env python3
"""
전체 맵 일괄 임베딩 스크립트
SQLite DB에서 모든 맵을 로드하고 임베딩을 생성하여 FAISS 인덱스를 구축합니다.

Usage:
    python build_all_embeddings.py <faiss_index_path> <db_path> [--rebuild]

Options:
    --rebuild: 기존 인덱스를 삭제하고 처음부터 다시 구축

Output (stdout):
    JSON: {
        "success": true,
        "total_maps": 10,
        "embedded_count": 8,
        "skipped_count": 2,
        "embedding_model": "text-embedding-3-small",
        "index_path": "..."
    }
"""

import sys
import json
import sqlite3
import shutil
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
    print(f"INFO: {message}", file=sys.stderr)


def log_progress(message):
    """진행 상황 로그"""
    print(f"PROGRESS: {message}", file=sys.stderr)


def load_all_maps(db_path, only_not_embedded=False):
    """
    SQLite DB에서 모든 맵 로드

    Args:
        db_path: SQLite DB 파일 경로
        only_not_embedded: True면 is_embedded=0인 맵만 로드

    Returns:
        list: 맵 정보 리스트
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if only_not_embedded:
        query = """
            SELECT id, name, description, tags, category, difficulty
            FROM maps
            WHERE is_embedded = 0
            ORDER BY id
        """
    else:
        query = """
            SELECT id, name, description, tags, category, difficulty
            FROM maps
            ORDER BY id
        """

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def update_embedding_status_batch(db_path, map_ids, embedding_model):
    """
    여러 맵의 임베딩 상태를 일괄 업데이트

    Args:
        db_path: SQLite DB 파일 경로
        map_ids: 맵 ID 리스트
        embedding_model: 사용된 임베딩 모델명
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    for map_id in map_ids:
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


def build_all_embeddings(faiss_index_path, db_path, rebuild=False):
    """
    전체 맵 임베딩 일괄 생성

    Args:
        faiss_index_path: FAISS 인덱스 저장 경로
        db_path: SQLite DB 경로
        rebuild: 기존 인덱스 삭제 여부

    Returns:
        dict: 결과 요약
    """
    embedding_model_name = "text-embedding-3-small"
    embeddings = OpenAIEmbeddings(model=embedding_model_name)

    faiss_path = Path(faiss_index_path)

    # Rebuild 옵션: 기존 인덱스 삭제
    if rebuild and faiss_path.exists():
        log_progress(f"Removing existing FAISS index: {faiss_index_path}")
        shutil.rmtree(faiss_path)

    # 맵 로드 (rebuild이면 전체, 아니면 미임베딩만)
    only_not_embedded = not rebuild
    maps = load_all_maps(db_path, only_not_embedded=only_not_embedded)

    total_maps = len(maps)

    if total_maps == 0:
        log_progress("No maps to embed.")
        return {
            'success': True,
            'totalMaps': 0,
            'embeddedCount': 0,
            'skippedCount': 0,
            'embeddingModel': embedding_model_name,
            'indexPath': faiss_index_path
        }

    log_progress(f"Found {total_maps} map(s) to embed.")

    # Document 리스트 생성
    documents = []
    map_ids = []

    for i, map_data in enumerate(maps, 1):
        log_progress(f"[{i}/{total_maps}] Processing: {map_data['name']}")

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

        documents.append(doc)
        map_ids.append(map_data['id'])

    # FAISS 인덱스 생성 또는 업데이트
    if faiss_path.exists() and not rebuild:
        # 기존 인덱스에 추가
        log_progress(f"Loading existing FAISS index from {faiss_index_path}")
        vector_store = FAISS.load_local(
            faiss_index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

        log_progress(f"Adding {len(documents)} documents to existing index...")
        vector_store.add_documents(documents)
    else:
        # 새 인덱스 생성
        log_progress(f"Creating new FAISS index with {len(documents)} documents...")
        faiss_path.mkdir(parents=True, exist_ok=True)
        vector_store = FAISS.from_documents(documents, embeddings)

    # 인덱스 저장
    log_progress(f"Saving FAISS index to {faiss_index_path}")
    vector_store.save_local(faiss_index_path)

    # DB 업데이트
    log_progress(f"Updating database embedding status for {len(map_ids)} maps...")
    update_embedding_status_batch(db_path, map_ids, embedding_model_name)

    log_progress("✅ All embeddings completed successfully!")

    return {
        'success': True,
        'totalMaps': total_maps,
        'embeddedCount': len(map_ids),
        'skippedCount': 0,
        'embeddingModel': embedding_model_name,
        'indexPath': faiss_index_path
    }


def main():
    if len(sys.argv) < 3:
        log_error("Usage: python build_all_embeddings.py <faiss_index_path> <db_path> [--rebuild]")
        sys.exit(1)

    try:
        faiss_index_path = sys.argv[1]
        db_path = sys.argv[2]
        rebuild = '--rebuild' in sys.argv

        if rebuild:
            log_progress("⚠️  Rebuild mode: existing index will be deleted")

        result = build_all_embeddings(faiss_index_path, db_path, rebuild)

        # stdout으로 JSON 출력
        print(json.dumps(result, ensure_ascii=False))

    except Exception as e:
        log_error(f"Failed to build embeddings: {e}")
        import traceback
        traceback.print_exc(file=sys.stderr)

        error_result = {
            'success': False,
            'error': str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)


if __name__ == "__main__":
    main()
