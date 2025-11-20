"""
OpenAI API 키 테스트 스크립트
"""
from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
print(f"API 키 로드됨: {api_key[:20]}...{api_key[-4:]}")
print(f"API 키 길이: {len(api_key)}")

try:
    client = OpenAI(api_key=api_key)

    # 간단한 임베딩 테스트
    print("\n임베딩 API 테스트 중...")
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input="테스트 문장입니다."
    )
    print("✓ 성공! API 키가 정상 작동합니다.")
    print(f"  임베딩 차원: {len(response.data[0].embedding)}")

except Exception as e:
    print(f"✗ 오류 발생: {e}")
    print("\n해결 방법:")
    print("1. API 키가 올바른지 확인하세요")
    print("2. https://platform.openai.com/account/billing 에서 결제 정보 등록")
    print("3. API 키를 새로 생성해보세요")
