import json

with open('data/candidates.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 통합된 전남광주통합특별시 항목 생성
tonghap = {
    "id": "jeonnam-gwangju",
    "region": "전남광주통합특별시",
    "title": "전남광주통합특별시장",
    "emoji": "🌸",
    "verdict": "minjoo_strong",
    "candidates": [
        {
            "name": "민형배",
            "party": "minjoo",
            "partyName": "더불어민주당",
            "status": "공천확정",
            "age": "57세 (1969년생)",
            "current": "국회의원(광주 광산을)",
            "education": "전남대 정치외교학과",
            "career": "21·22대 국회의원, 광산구청장",
            "pledge": "AI 클러스터 완성, 광주형 일자리 확대, 해상풍력 선도",
            "pct": 70.0
        },
        {
            "name": "이정현",
            "party": "gukmin",
            "partyName": "국민의힘",
            "status": "공천확정",
            "age": "60세 (1966년생)",
            "current": "전 국회의원",
            "education": "조선대 정치외교학과",
            "career": "19·20대 국회의원, 국민의힘 대표",
            "pledge": "지역 경제 활성화, 기업 유치",
            "pct": 5.0
        },
        {
            "name": "강은미",
            "party": "jeongui",
            "partyName": "정의당",
            "status": "공천확정",
            "age": "—",
            "current": "전 국회의원",
            "education": "—",
            "career": "21대 국회의원",
            "pledge": "노동·복지 중심 통합특별시 건설",
            "pct": None
        }
    ],
    "surveyDate": "2026.04.25",
    "surveyOrg": "연합뉴스",
    "sampleSize": "1,000명",
    "history": [
        {
            "date": "2026.04.25",
            "org": "연합뉴스",
            "pcts": [70.0, 5.0, None],
            "gap": "+65.0%p",
            "sample": "1,000명"
        }
    ]
}

# 기존 gwangju(인덱스4)를 통합 항목으로 교체, jeonnam(인덱스13) 제거
new_gwangyeok = []
for r in data['gwangyeok']:
    if r['id'] == 'gwangju':
        new_gwangyeok.append(tonghap)
    elif r['id'] == 'jeonnam':
        continue  # 전남 항목 제거
    else:
        new_gwangyeok.append(r)

data['gwangyeok'] = new_gwangyeok

with open('data/candidates.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("완료: 광주+전남 → 전남광주통합특별시 통합")
print(f"광역단체 수: {len(data['gwangyeok'])}개 (기존 17개 → 16개)")
