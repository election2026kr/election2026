#!/usr/bin/env python3
"""
2026-05-19 v3 업데이트 스크립트
- 서울시장: 메트릭스(조선일보) 5.16~17 수치 추가 (정원오 40%, 오세훈 37%)
- 부산시장: 메트릭스(조선일보) 5.16~17 수치 추가 (전재수 44%, 박형준 35%)
- 대구시장: 메트릭스(조선일보) 5.16~17 수치 추가 (김부겸 40%, 추경호 38%)
- 경남도지사: 메트릭스(조선일보) 5.16~17 수치 업데이트 (김경수 44%, 박완수 34%)
  + 이너텍시스템즈(프레시안) 5.17~18 수치 추가 (김경수 41.9%, 박완수 44.7%)
- 울산시장: 단일화 합의 현황 note 업데이트 (5.23~24 여론조사 예정)
"""
import json

with open('data/candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 메타 업데이트
data['meta']['version'] = '2026-05-19-v3'
data['meta']['lastUpdated'] = '2026-05-19'
data['meta']['source'] = (
    '중앙선거여론조사심의위원회 / 메트릭스(조선일보 의뢰) / 코리아리서치(MBC 의뢰) / '
    '한국리서치(KBS 의뢰) / 한국갤럽(뉴스1 의뢰) / 한국갤럽(동아일보 의뢰) / '
    '조원씨앤아이(스트레이트뉴스 의뢰) / 한길리서치(부산MBC 의뢰) / KSOI(CBS 의뢰) / '
    '여론조사꽃 / 여론조사공정(KBS울산방송·울산매일신문 의뢰) / MBC경남(여론조사꽃 의뢰) / '
    '이너텍시스템즈(프레시안 의뢰) / 연합뉴스 / 뉴시스 / 동아일보 / KBS 보도'
)

for region in data['gwangyeok']:
    # 서울시장: 메트릭스 조선일보 5.16~17 수치 추가 (history에 추가)
    if region['id'] == 'seoul':
        # 현재 최신 수치는 코리아리서치(MBC) 43% vs 35%로 유지
        # 메트릭스 조선일보 수치를 history에 추가
        new_entry = {
            "date": "2026.05.16~17",
            "org": "메트릭스(조선일보 의뢰)",
            "pcts": [40.0, 37.0],
            "gap": "+3.0%p (오차범위 내 초접전)",
            "sample": "800명"
        }
        # 이미 있는지 확인
        existing_dates_orgs = [(h['date'], h['org']) for h in region.get('history', [])]
        if (new_entry['date'], new_entry['org']) not in existing_dates_orgs:
            region['history'].insert(0, new_entry)
            print(f"서울 history에 메트릭스 수치 추가")

    # 부산시장: 메트릭스 조선일보 5.16~17 수치 추가
    elif region['id'] == 'busan':
        new_entry = {
            "date": "2026.05.16~17",
            "org": "메트릭스(조선일보 의뢰)",
            "pcts": [44.0, 35.0],
            "gap": "+9.0%p (오차범위 밖 민주 우세)",
            "sample": "800명"
        }
        existing_dates_orgs = [(h['date'], h['org']) for h in region.get('history', [])]
        if (new_entry['date'], new_entry['org']) not in existing_dates_orgs:
            region['history'].insert(0, new_entry)
            print(f"부산 history에 메트릭스 수치 추가")

    # 대구시장: 메트릭스 조선일보 5.16~17 수치 추가
    elif region['id'] == 'daegu':
        new_entry = {
            "date": "2026.05.16~17",
            "org": "메트릭스(조선일보 의뢰)",
            "pcts": [40.0, 38.0],
            "gap": "+2.0%p (오차범위 내 초접전)",
            "sample": "800명"
        }
        existing_dates_orgs = [(h['date'], h['org']) for h in region.get('history', [])]
        if (new_entry['date'], new_entry['org']) not in existing_dates_orgs:
            region['history'].insert(0, new_entry)
            print(f"대구 history에 메트릭스 수치 추가")

    # 경남도지사: 이너텍시스템즈(프레시안) 5.17~18 수치 추가
    elif region['id'] == 'gyeongnam':
        new_entry = {
            "date": "2026.05.17~18",
            "org": "이너텍시스템즈(프레시안 의뢰)",
            "pcts": [41.9, 44.7],
            "gap": "-2.8%p (오차범위 내 접전, 박완수 소폭 우세)",
            "sample": "1,022명"
        }
        existing_dates_orgs = [(h['date'], h['org']) for h in region.get('history', [])]
        if (new_entry['date'], new_entry['org']) not in existing_dates_orgs:
            region['history'].insert(0, new_entry)
            print(f"경남 history에 이너텍시스템즈 수치 추가")

    # 울산시장: 단일화 현황 note 업데이트 (pct 유지, note 추가)
    elif region['id'] == 'ulsan':
        for c in region['candidates']:
            if c['party'] == 'minjoo':
                c['status'] = '공천확정 (단일화 여론조사 5.23~24 예정)'
            elif c['party'] == 'jinbo':
                c['status'] = '공천확정 (단일화 여론조사 5.23~24 예정)'
        print(f"울산시장 단일화 현황 업데이트")

with open('data/candidates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("candidates.json 업데이트 완료")
