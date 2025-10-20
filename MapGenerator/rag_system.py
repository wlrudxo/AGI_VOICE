"""
LangChain 기반 SUMO 맵 추천 RAG 시스템
맵 설명 텍스트를 임베딩하여 유사한 맵을 검색합니다.
"""

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import os
from pathlib import Path
from dotenv import load_dotenv

# .env 파일에서 환경변수 로드
load_dotenv()


class MapRAG:
    def __init__(self, api_key=None):
        """
        RAG 시스템 초기화

        Args:
            api_key: OpenAI API 키 (환경변수 OPENAI_API_KEY 사용 가능)
        """
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key

        self.embedding = OpenAIEmbeddings()
        self.db = None
        self.llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)
        self.db_path = "faiss_map_db"

    def load_map_descriptions(self, file_path="map_descriptions.txt"):
        """
        map_descriptions.txt 파일을 로드하여 Document 객체 리스트로 변환

        Returns:
            list: LangChain Document 객체들
        """
        documents = []
        current_map = None
        current_description = []

        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if line.startswith("=====") and line.endswith("====="):
                    # 이전 맵 저장
                    if current_map and current_description:
                        description_text = " ".join(current_description).strip()
                        doc = Document(
                            page_content=description_text,
                            metadata={
                                "map_name": current_map,
                                "nod_file": f"{current_map}.nod.xml",
                                "edg_file": f"{current_map}.edg.xml"
                            }
                        )
                        documents.append(doc)

                    # 새 맵 시작
                    parts = line.strip("= ").split("(")
                    if len(parts) == 2:
                        current_map = parts[1].strip(")")
                        current_description = []
                elif current_map and line:
                    current_description.append(line)

            # 마지막 맵 저장
            if current_map and current_description:
                description_text = " ".join(current_description).strip()
                doc = Document(
                    page_content=description_text,
                    metadata={
                        "map_name": current_map,
                        "nod_file": f"{current_map}.nod.xml",
                        "edg_file": f"{current_map}.edg.xml"
                    }
                )
                documents.append(doc)

        return documents

    def build_vector_db(self):
        """
        맵 설명을 임베딩하고 FAISS 벡터 DB 생성
        """
        print("맵 설명 파일 로드 중...")
        documents = self.load_map_descriptions()

        print(f"{len(documents)}개의 맵 발견. 임베딩 생성 중...")

        # FAISS 벡터 DB 생성
        self.db = FAISS.from_documents(documents, self.embedding)

        # 로컬에 저장
        self.db.save_local(self.db_path)
        print(f"벡터 DB 저장 완료: {self.db_path}")

    def load_vector_db(self):
        """
        저장된 FAISS 벡터 DB 로드
        """
        if not Path(self.db_path).exists():
            raise FileNotFoundError(
                f"{self.db_path}를 찾을 수 없습니다. "
                "먼저 build_vector_db()를 실행하세요."
            )

        self.db = FAISS.load_local(
            self.db_path,
            self.embedding,
            allow_dangerous_deserialization=True
        )
        print(f"벡터 DB 로드 완료: {self.db_path}")

    def search_similar_maps(self, query, top_k=3):
        """
        사용자 쿼리와 유사한 맵 검색

        Args:
            query: 사용자 쿼리 문자열
            top_k: 반환할 상위 맵 개수

        Returns:
            list: [(Document, similarity_score), ...]
        """
        if self.db is None:
            self.load_vector_db()

        # 유사도 검색
        results = self.db.similarity_search_with_score(query, k=top_k)

        print(f"\n쿼리: '{query}'")
        print("유사한 맵:")
        for doc, score in results:
            print(f"  - {doc.metadata['map_name']} (거리: {score:.4f})")
            print(f"    {doc.page_content[:80]}...")

        return results

    def read_map_xml(self, map_name):
        """
        맵의 XML 파일들을 읽어옴

        Args:
            map_name: 맵 이름

        Returns:
            dict: {"nod_xml": content, "edg_xml": content}
        """
        result = {}

        nod_file = Path(f"{map_name}.nod.xml")
        edg_file = Path(f"{map_name}.edg.xml")

        if nod_file.exists():
            with open(nod_file, 'r', encoding='utf-8') as f:
                result["nod_xml"] = f.read()

        if edg_file.exists():
            with open(edg_file, 'r', encoding='utf-8') as f:
                result["edg_xml"] = f.read()

        return result

    def generate_map_with_ai(self, user_query, top_k=2):
        """
        RAG를 사용하여 AI가 맵을 생성하도록 프롬프트 구성

        Args:
            user_query: 사용자의 맵 요청
            top_k: 참고할 예시 맵 개수

        Returns:
            str: AI 생성 프롬프트 (실제 AI 호출은 별도)
        """
        if self.db is None:
            self.load_vector_db()

        # 유사한 맵 검색
        similar_docs = self.search_similar_maps(user_query, top_k)

        # 프롬프트 구성
        prompt = f"사용자 요청: {user_query}\n\n"
        prompt += "=== 참고할 유사한 맵 예시들 ===\n\n"

        for i, (doc, score) in enumerate(similar_docs, 1):
            map_name = doc.metadata['map_name']

            prompt += f"[예시 {i}] {map_name}\n"
            prompt += f"설명: {doc.page_content}\n\n"

            # XML 파일 내용 추가
            xml_content = self.read_map_xml(map_name)

            if "nod_xml" in xml_content:
                prompt += f"Node 파일:\n```xml\n{xml_content['nod_xml']}\n```\n\n"

            if "edg_xml" in xml_content:
                prompt += f"Edge 파일:\n```xml\n{xml_content['edg_xml']}\n```\n\n"

            prompt += "-" * 60 + "\n\n"

        prompt += """위 예시들을 참고하여, 사용자가 요청한 맵의 node.xml과 edge.xml을 생성해주세요.

요구사항:
1. SUMO 형식을 정확히 따를 것
2. 노드 좌표가 실제 도로 형태에 맞게 배치될 것
3. Edge는 올바른 노드 연결 관계를 가질 것
4. 적절한 차선 수(numLanes)와 속도 제한(speed)을 설정할 것

출력 형식:
=== node.xml ===
[XML 내용]

=== edge.xml ===
[XML 내용]
"""

        return prompt

    def get_top_maps(self, query, k=3):
        """
        간단하게 상위 k개 맵 이름만 반환

        Args:
            query: 사용자 쿼리
            k: 반환할 맵 개수

        Returns:
            list: 맵 이름 리스트
        """
        results = self.search_similar_maps(query, k)
        return [doc.metadata['map_name'] for doc, _ in results]


def main():
    """
    사용 예시
    """
    print("=" * 60)
    print("SUMO 맵 RAG 시스템 (LangChain)")
    print("=" * 60)

    rag = MapRAG()

    # 1. 벡터 DB 생성 (최초 1회만)
    print("\n[1단계] 벡터 DB 생성")
    rag.build_vector_db()

    # 2. 검색 테스트
    print("\n" + "=" * 60)
    print("[2단계] 유사 맵 검색 테스트")
    print("=" * 60)

    test_queries = [
        "삼거리 도로가 필요해",
        "고속도로 진입로 만들어줘",
        "신호등 있는 사거리",
        "넓은 3차선 도로"
    ]

    for query in test_queries:
        top_maps = rag.get_top_maps(query, k=2)
        print()

    # 3. AI 프롬프트 생성
    print("\n" + "=" * 60)
    print("[3단계] AI 맵 생성 프롬프트")
    print("=" * 60)

    user_request = "곡선이 있는 T자 교차로"
    prompt = rag.generate_map_with_ai(user_request, top_k=2)

    print(f"\n생성된 프롬프트 미리보기 (처음 800자):")
    print(prompt[:800])
    print("...\n")

    # 전체 프롬프트를 파일로 저장
    with open("ai_prompt_example.txt", 'w', encoding='utf-8') as f:
        f.write(prompt)
    print("전체 프롬프트 저장: ai_prompt_example.txt")


if __name__ == "__main__":
    main()
