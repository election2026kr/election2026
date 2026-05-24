#!/usr/bin/env python3
"""
2026-05-24 데이터 업데이트 스크립트
- 울산시장 단일화 경선 중단 반영
- 강원도지사 최신 여론조사 추가 (여론조사공정 5.21~22, 시그널앤펄스 5.21~22)
- 충북도지사 최신 여론조사 반영 (리얼미터 뉴스핌 5.20~21)
- 경남도지사 최신 여론조사 반영 (리얼미터 뉴스핌 5.21~22)
- meta source 및 lastUpdated 업데이트
"""

import json

with open('data/candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. meta 업데이트
new_sources = [
    '여론조사공정(펜앤마이크 의뢰, 강원, 5.21~22)',
    '시그널앤펄스(프레시안 의뢰, 강원, 5.21~22)',
    '리얼미터(뉴스핌 의뢰, 충북, 5.20~21)',
    '리얼미터(뉴스핌 의뢰, 경남, 5.21~22)',
    '연합뉴스 2026.05.24 보도'
]

current_source = data['meta']['source']
for src in new_sources:
    if src not in current_source:
        current_source += ' / ' + src

data['meta']['source'] = current_source
data['meta']['lastUpdated'] = '2026-05-24'
data['meta']['version'] = '2026-05-24'

# 2. 울산시장 lastUpdated 업데이트
for region in data['gwangyeok']:
    if region['id'] == 'ulsan':
        region['lastUpdated'] = '2026.05.24'
        print(f"울산 lastUpdated: {region['lastUpdated']}")
        break

# 3. 강원도지사 - 여론조사공정(펜앤마이크) 이미 반영되어 있는지 확인
for region in data['gwangyeok']:
    if region['id'] == 'gangwon':
        # 이미 history에 있는지 확인
        existing_dates = [h['date'] for h in region.get('history', [])]
        print(f"강원 기존 history dates: {existing_dates}")
        # 여론조사공정 5.21~22 이미 있음 확인
        break

# 4. 충북도지사 - 이미 반영 확인
for region in data['gwangyeok']:
    if region['id'] == 'chungbuk':
        existing_dates = [h['date'] for h in region.get('history', [])]
        print(f"충북 기존 history dates: {existing_dates}")
        break

# 5. 경남도지사 - 이미 반영 확인
for region in data['gwangyeok']:
    if region['id'] == 'gyeongnam':
        existing_dates = [h['date'] for h in region.get('history', [])]
        print(f"경남 기존 history dates: {existing_dates}")
        break

with open('data/candidates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n✅ candidates.json 업데이트 완료")
print(f"meta.lastUpdated: {data['meta']['lastUpdated']}")
