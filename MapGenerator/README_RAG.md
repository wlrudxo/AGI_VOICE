# SUMO 맵 RAG 시스템 사용법

LangChain과 OpenAI Embeddings를 사용한 맵 추천 시스템입니다.

## 설치

```bash
pip install -r requirements.txt
```

## API 키 설정

```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

## 사용법

### 1. 벡터 DB 생성 (최초 1회)

```python
from rag_system import MapRAG

rag = MapRAG()
rag.build_vector_db()  # map_descriptions.txt를 읽어서 FAISS DB 생성
```

### 2. 유사한 맵 검색

```python
rag = MapRAG()
results = rag.search_similar_maps("삼거리 도로가 필요해", top_k=3)

# 맵 이름만 간단히 받기
map_names = rag.get_top_maps("고속도로 진입로", k=2)
print(map_names)  # ['merge_lane', 'three_lane_road']
```

### 3. AI 프롬프트 생성

```python
rag = MapRAG()
prompt = rag.generate_map_with_ai("곡선이 있는 T자 교차로", top_k=2)

# 이 프롬프트를 GPT-4 등에 전달하여 맵 생성
```

## 전체 실행

```bash
python rag_system.py
```

이 명령으로:
1. 벡터 DB 생성
2. 테스트 쿼리 실행
3. AI 프롬프트 예시 생성

## 파일 구조

- `map_descriptions.txt`: 맵 설명 텍스트 (임베딩 소스)
- `faiss_map_db/`: FAISS 벡터 DB (자동 생성)
- `*.nod.xml, *.edg.xml`: SUMO 맵 파일들
- `rag_system.py`: RAG 시스템 메인 코드

## 워크플로우

```
사용자 입력 → 임베딩 → FAISS 검색 → 유사 맵 발견 → XML 로드 → AI 프롬프트 생성
```
