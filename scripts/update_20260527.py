#!/usr/bin/env python3
"""
2026-05-27 데이터 업데이트 스크립트
주요 변경:
1. 대전시장 — 알앤써치(뉴스핌 의뢰, 5.24) 이장우 46.5% vs 허태정 45.6% 추가 → verdict 'close'
2. 충남도지사 — 리얼미터(굿모닝충청 의뢰, 5.22~23) 박수현 49.3% vs 김태흠 38.5% 추가
3. 판세 요약 업데이트 (대전 close 반영)
4. 메타 버전 업데이트
"""
import json
import re

CANDIDATES_PATH = '/home/ubuntu/election2026/data/candidates.json'
INDEX_PATH = '/home/ubuntu/election2026/index.html'

# ===== candidates.json 업데이트 =====
with open(CANDIDATES_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 1. 대전시장 업데이트: verdict → close, pct 업데이트, 신규 조사 추가
for region in data['gwangyeok']:
    if region['id'] == 'daejeon':
        # verdict 변경
        region['verdict'] = 'close'
        # 후보 pct 업데이트 (알앤써치 기준)
        for cand in region['candidates']:
            if cand['name'] == '허태정':
                cand['pct'] = 45.6
            elif cand['name'] == '이장우':
                cand['pct'] = 46.5
        # surveyDate, surveyOrg, sampleSize 업데이트
        region['surveyDate'] = '2026.05.24'
        region['surveyOrg'] = '알앤써치(뉴스핌 의뢰)'
        region['sampleSize'] = '약 1,000명'
        # history 맨 앞에 신규 조사 추가
        new_survey = {
            "date": "2026.05.24",
            "org": "알앤써치(뉴스핌 의뢰)",
            "pcts": [45.6, 46.5],
            "gap": "-0.9%p (오차범위 내 초박빙, 이장우 소폭 우세, ±3.5%p) / 사전투표층 허태정 66.6% vs 이장우 27.1% / 본투표층 이장우 64.7% vs 허태정 29.5%",
            "sample": "약 1,000명"
        }
        region['history'].insert(0, new_survey)
        region['lastUpdated'] = '2026.05.27'
        print(f"[대전시장] verdict→close, 알앤써치 조사 추가 완료")

# 2. 충남도지사 — 리얼미터(굿모닝충청 의뢰, 5.22~23) 이미 반영됨 확인
# candidates.json에 이미 5.22~23 리얼미터 조사가 있으나,
# 최신 조사(5.22~23)의 pct가 49.3/38.5로 반영되어 있음 → 현재 surveyDate는 5.24~25 코리아리서치
# 코리아리서치(대전MBC) 5.24~25 조사가 더 최신이므로 유지하되,
# 리얼미터(굿모닝충청) 5.22~23 조사를 history에 추가 (이미 있는지 확인)
for region in data['gwangyeok']:
    if region['id'] == 'chungnam':
        # 이미 5.22~23 리얼미터 조사가 있는지 확인
        existing_dates = [h.get('date', '') for h in region.get('history', [])]
        if '2026.05.22~23' not in existing_dates:
            new_survey = {
                "date": "2026.05.22~23",
                "org": "리얼미터(굿모닝충청 의뢰)",
                "pcts": [49.3, 38.5],
                "gap": "+10.8%p (오차범위 밖 민주 우세, ±3.5%p)",
                "sample": "803명"
            }
            # 5.24~25 다음에 삽입
            region['history'].insert(1, new_survey)
            print(f"[충남도지사] 리얼미터(굿모닝충청) 5.22~23 조사 추가 완료")
        else:
            print(f"[충남도지사] 리얼미터(굿모닝충청) 5.22~23 조사 이미 존재")
        region['lastUpdated'] = '2026.05.27'

# 3. 메타 버전 업데이트
data['meta']['version'] = '2026-05-27'
data['meta']['lastUpdated'] = '2026-05-27'
# 출처 추가
new_source = ' / 알앤써치(뉴스핌 의뢰, 대전, 5.24) / 리얼미터(굿모닝충청 의뢰, 충남, 5.22~23) / KBS-한국리서치(서울·부산·대구, 5.21~25) / KSOI(CBS 의뢰, 대구, 5.24~25) / 한길리서치(새전북신문 의뢰, 전북, 5.21~22)'
if new_source not in data['meta']['source']:
    data['meta']['source'] += new_source

# 저장
with open(CANDIDATES_PATH, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("candidates.json 업데이트 완료")

# ===== index.html 업데이트 =====
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 대전 판세 지도: minjoo-win → close-race
old_daejeon_map = '<div class="region-block minjoo-win" style="grid-column:3;grid-row:2;cursor:pointer;" onclick="location.href=\'pages/gwangyeok/daejeon.html\'">          <div class="r-name">대전시장</div><div class="r-cand">허태정(민주)</div>'
new_daejeon_map = '<div class="region-block close-race" style="grid-column:3;grid-row:2;cursor:pointer;" onclick="location.href=\'pages/gwangyeok/daejeon.html\'">          <div class="r-name">대전시장</div><div class="r-cand">접전 (민주·국힘)</div>'
if old_daejeon_map in html:
    html = html.replace(old_daejeon_map, new_daejeon_map)
    print("[index.html] 대전 판세 지도 업데이트: minjoo-win → close-race")
else:
    print("[index.html] 대전 판세 지도 패턴 미발견 (이미 업데이트됐을 수 있음)")

# 2. 충북 판세 지도: minjoo-win → close-race (충북도 접전 양상)
old_chungbuk_map = '<div class="region-block minjoo-win" style="grid-column:2;grid-row:2;cursor:pointer;" onclick="location.href=\'pages/gwangyeok/chungbuk.html\'">          <div class="r-name">충북도지사</div><div class="r-cand">신용한(민주)</div>'
new_chungbuk_map = '<div class="region-block close-race" style="grid-column:2;grid-row:2;cursor:pointer;" onclick="location.href=\'pages/gwangyeok/chungbuk.html\'">          <div class="r-name">충북도지사</div><div class="r-cand">접전 (민주·국힘)</div>'
if old_chungbuk_map in html:
    html = html.replace(old_chungbuk_map, new_chungbuk_map)
    print("[index.html] 충북 판세 지도 업데이트: minjoo-win → close-race")
else:
    print("[index.html] 충북 판세 지도 패턴 미발견 (이미 업데이트됐을 수 있음)")

# 3. 판세 요약 칩 업데이트
# 대전 close 반영: 민주 우세 7(압승 1), 국힘 우세 1, 접전 8
old_summary = '<span class="sum-chip chip-minjoo">민주 우세 8(압승 1)</span>\n            <span class="sum-chip chip-gukmin">국힘 우세 1</span>\n            <span class="sum-chip chip-close">접전 7</span>'
new_summary = '<span class="sum-chip chip-minjoo">민주 우세 7(압승 1)</span>\n            <span class="sum-chip chip-gukmin">국힘 우세 1</span>\n            <span class="sum-chip chip-close">접전 8</span>'
if old_summary in html:
    html = html.replace(old_summary, new_summary)
    print("[index.html] 판세 요약 칩 업데이트: 민주 우세 8→7, 접전 7→8")
else:
    print("[index.html] 판세 요약 칩 패턴 미발견")

# 4. 여론조사 요약 칩 업데이트
old_survey_chip = '민주 우세 8 (압승 1 포함)'
new_survey_chip = '민주 우세 7 (압승 1 포함)'
if old_survey_chip in html:
    html = html.replace(old_survey_chip, new_survey_chip)
    print("[index.html] 여론조사 요약 칩 업데이트: 민주 우세 8→7")
else:
    print("[index.html] 여론조사 요약 칩 패턴 미발견")

old_close_chip = '오차범위 내 접전 7'
new_close_chip = '오차범위 내 접전 8'
if old_close_chip in html:
    html = html.replace(old_close_chip, new_close_chip)
    print("[index.html] 여론조사 요약 칩 접전 업데이트: 7→8")
else:
    print("[index.html] 여론조사 요약 칩 접전 패턴 미발견")

# 5. 대전 빅매치 카드 업데이트 (격전지 섹션)
# 대전 카드 수치 업데이트: 허태정 45.6%, 이장우 46.5%
old_daejeon_card_pct1 = '<div class="candidate-pct" style="color:#6ea8fe">44.0%</div>\n      </div>\n      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:44.0%"></div></div></div>\n      <div class="candidate-row" style="margin-top:6px;">\n        <div class="candidate-avatar avatar-gukmin" onclick="openCandModal(\'김태흠\''
# 이 패턴은 충남 카드와 겹칠 수 있어 더 구체적인 패턴 사용
# 대전 격전지 카드 전체를 찾아서 교체
old_daejeon_bigmatch = '''    <div class="match-card">
      <div class="region-tag"><span>🔬 대전광역시장</span><span class="verdict-badge badge-minjoo">민주 우세</span></div>
      <div class="candidate-row">
        <div class="candidate-avatar avatar-minjoo" onclick="openCandModal(\'허태정\',\'minjoo\',\'61세 (1965년생)\',\'전 대전시장\',\'대전광역시\',\'고려대 정책대학원\',\'대전 유성구청장(2010~2018), 대전시장(2018~2022)\',\'대전 과학기술 허브 완성, 대덕특구 혁신\')">허</div>
        <div class="candidate-info" onclick="openCandModal(\'허태정\',\'minjoo\',\'61세 (1965년생)\',\'전 대전시장\',\'대전광역시\',\'고려대 정책대학원\',\'대전 유성구청장(2010~2018), 대전시장(2018~2022)\',\'대전 과학기술 허브 완성, 대덕특구 혁신\')" style="cursor:pointer"><div class="candidate-name">허태정</div><div class="candidate-party">더불어민주당</div></div>
        <div class="candidate-pct" style="color:#6ea8fe">44.0%</div>
      </div>
      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:44.0%"></div></div></div>
      <div class="candidate-row" style="margin-top:6px;">
        <div class="candidate-avatar avatar-gukmin" onclick="openCandModal(\'이장우\',\'gukmin\',\'61세 (1965년생)\',\'대전광역시장(현)\',\'대전광역시\',\'대전대 행정학 박사\',\'19·20대 국회의원, 대전시장(2022~현재)\',\'대전 스마트시티 구축, 교통 인프라 확충\')">이</div>
        <div class="candidate-info" onclick="openCandModal(\'이장우\',\'gukmin\',\'61세 (1965년생)\',\'대전광역시장(현)\',\'대전광역시\',\'대전대 행정학 박사\',\'19·20대 국회의원, 대전시장(2022~현재)\',\'대전 스마트시티 구축, 교통 인프라 확충\')" style="cursor:pointer"><div class="candidate-name">이장우</div><div class="candidate-party">국민의힘</div></div>
        <div class="candidate-pct" style="color:#ff8080">30.0%</div>
      </div>
      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:30.0%"></div></div></div>
      <div class="match-footer"><span class="survey-date">📅 2026.05.24~25 · 코리아리서치(대전MBC 의뢰)</span><span style="font-size:11px;color:#6ea8fe;">오차범위 밖 민주 우세 +9.0%p</span></div>
    </div>'''

new_daejeon_bigmatch = '''    <div class="match-card">
      <div class="region-tag"><span>🔬 대전광역시장</span><span class="verdict-badge badge-close">오차범위 내 초박빙</span></div>
      <div class="candidate-row">
        <div class="candidate-avatar avatar-minjoo" onclick="openCandModal(\'허태정\',\'minjoo\',\'61세 (1965년생)\',\'전 대전시장\',\'대전광역시\',\'고려대 정책대학원\',\'대전 유성구청장(2010~2018), 대전시장(2018~2022)\',\'대전 과학기술 허브 완성, 대덕특구 혁신\')">허</div>
        <div class="candidate-info" onclick="openCandModal(\'허태정\',\'minjoo\',\'61세 (1965년생)\',\'전 대전시장\',\'대전광역시\',\'고려대 정책대학원\',\'대전 유성구청장(2010~2018), 대전시장(2018~2022)\',\'대전 과학기술 허브 완성, 대덕특구 혁신\')" style="cursor:pointer"><div class="candidate-name">허태정</div><div class="candidate-party">더불어민주당</div></div>
        <div class="candidate-pct" style="color:#6ea8fe">45.6%</div>
      </div>
      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:45.6%"></div></div></div>
      <div class="candidate-row" style="margin-top:6px;">
        <div class="candidate-avatar avatar-gukmin" onclick="openCandModal(\'이장우\',\'gukmin\',\'61세 (1965년생)\',\'대전광역시장(현)\',\'대전광역시\',\'대전대 행정학 박사\',\'19·20대 국회의원, 대전시장(2022~현재)\',\'대전 스마트시티 구축, 교통 인프라 확충\')">이</div>
        <div class="candidate-info" onclick="openCandModal(\'이장우\',\'gukmin\',\'61세 (1965년생)\',\'대전광역시장(현)\',\'대전광역시\',\'대전대 행정학 박사\',\'19·20대 국회의원, 대전시장(2022~현재)\',\'대전 스마트시티 구축, 교통 인프라 확충\')" style="cursor:pointer"><div class="candidate-name">이장우</div><div class="candidate-party">국민의힘</div></div>
        <div class="candidate-pct" style="color:#ff8080">46.5%</div>
      </div>
      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:46.5%"></div></div></div>
      <div class="match-footer"><span class="survey-date">📅 2026.05.24 · 알앤써치(뉴스핌 의뢰)</span><span style="font-size:11px;color:#aaa;">오차범위 내 초박빙 -0.9%p (이장우 소폭 우세)</span></div>
    </div>'''

if old_daejeon_bigmatch in html:
    html = html.replace(old_daejeon_bigmatch, new_daejeon_bigmatch)
    print("[index.html] 대전 빅매치 카드 업데이트 완료")
else:
    print("[index.html] 대전 빅매치 카드 패턴 미발견 (수동 확인 필요)")

# 6. 푸터 날짜 및 버전 업데이트
old_footer = '공천 확정 보도 기준: 연합뉴스·뉴시스·KBS·MBC·뉴스1 2026.05.26 기준 | 수치는 최신 등록 조사 기준 (v16)'
new_footer = '공천 확정 보도 기준: 연합뉴스·뉴시스·KBS·MBC·뉴스1 2026.05.27 기준 | 수치는 최신 등록 조사 기준 (v17)'
if old_footer in html:
    html = html.replace(old_footer, new_footer)
    print("[index.html] 푸터 날짜/버전 업데이트: v16 → v17")
else:
    print("[index.html] 푸터 패턴 미발견")

# 7. polls.js 캐시 버스팅 업데이트
old_polls = 'js/polls.js?v=20260526-v4'
new_polls = 'js/polls.js?v=20260527-v1'
if old_polls in html:
    html = html.replace(old_polls, new_polls)
    print("[index.html] polls.js 캐시 버스팅 업데이트: v4 → v1(20260527)")
else:
    print("[index.html] polls.js 캐시 버스팅 패턴 미발견")

# 저장
with open(INDEX_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html 업데이트 완료")
print("\n=== 업데이트 완료 ===")
