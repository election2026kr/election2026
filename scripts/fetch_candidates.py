"""
선관위 OpenAPI 후보자 데이터 자동 수집 스크립트
GitHub Actions에서 매일 자정 실행
"""
import os
import json
import requests
from datetime import datetime

API_KEY = os.environ.get('NEC_API_KEY', '')
BASE_URL = 'https://apis.data.go.kr/9760000/CandsInfoInqireService'

def fetch_candidates():
    """선관위 API에서 후보자 정보 수집"""
    if not API_KEY:
        print("⚠️  NEC_API_KEY 환경변수가 없습니다. 기존 데이터를 유지합니다.")
        return None

    try:
        params = {
            'serviceKey': API_KEY,
            'pageNo': 1,
            'numOfRows': 1000,
            'sgId': '20260603',   # 2026년 6월 3일 선거
            'sgTypecode': '3',    # 지방선거
            '_type': 'json'
        }
        resp = requests.get(f'{BASE_URL}/getCandidateInfoInqire', params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        return None

def update_json(api_data):
    """수집된 데이터를 candidates.json에 반영"""
    json_path = 'data/candidates.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        current = json.load(f)

    # API 데이터가 없으면 기존 데이터 유지
    if not api_data:
        current['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        current['updateNote'] = 'API 연동 준비 중 — 수동 업데이트 기준'
    else:
        # TODO: API 응답 구조에 맞게 파싱 로직 추가
        current['lastUpdated'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        current['updateNote'] = '선관위 API 자동 업데이트'
        print(f"✅ 선관위 API 데이터 수집 완료")

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(current, f, ensure_ascii=False, indent=2)
    print(f"✅ {json_path} 업데이트 완료 ({current['lastUpdated']})")

if __name__ == '__main__':
    print(f"🔄 선관위 데이터 수집 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    api_data = fetch_candidates()
    update_json(api_data)
    print("✅ 완료!")
