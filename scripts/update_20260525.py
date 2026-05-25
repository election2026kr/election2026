#!/usr/bin/env python3
"""
2026-05-25 일일 데이터 업데이트 스크립트
주요 업데이트:
1. 경남도지사: 경남일보-리얼미터(5.18~19) 김경수 43.5% vs 박완수 43.2% history 추가
2. 충남도지사: 뉴스핌-리얼미터(5.18~19) 박수현 43.5% vs 김태흠 43.9% 수치 반영 (index.html 업데이트)
3. 울산시장: KBS-한국리서치(5.21~23) 4파전 및 단일화 상황 note 업데이트 (이미 반영됨 확인)
4. meta 정보 업데이트
5. index.html 충남 수치 업데이트 (KBS 41%:37% → 리얼미터 43.5%:43.9%)
"""

import json
import re
from pathlib import Path

BASE = Path(__file__).parent.parent
CANDIDATES = BASE / "data" / "candidates.json"
INDEX = BASE / "index.html"

# JSON 로드
with open(CANDIDATES, encoding="utf-8") as f:
    data = json.load(f)

changed = []

# ─── 1. 경남도지사: 경남일보-리얼미터(5.18~19) history 추가 ───
for region in data["gwangyeok"]:
    if region["id"] == "gyeongnam":
        # 이미 있는지 확인
        existing_dates = [h["date"] for h in region.get("history", [])]
        # 경남일보 리얼미터 5.18~19 (43.5 vs 43.2)는 이미 있음
        # 추가로 경남일보 2차 조사 (5.21~22 43.5 vs 43.2) 확인
        already_has_5_21_22_gyeongnamilbo = any(
            "경남일보" in h.get("org", "") and "21~22" in h.get("date", "")
            for h in region.get("history", [])
        )
        if not already_has_5_21_22_gyeongnamilbo:
            new_entry = {
                "date": "2026.05.21~22",
                "org": "리얼미터(경남일보 의뢰, 2차)",
                "pcts": [43.5, 43.2],
                "gap": "+0.3%p (오차범위 내 초접전, ±3.4%p)",
                "sample": "807명"
            }
            # history 맨 앞에 삽입
            region["history"].insert(0, new_entry)
            region["lastUpdated"] = "2026.05.25"
            changed.append("경남도지사: 경남일보-리얼미터(5.21~22) 43.5% vs 43.2% history 추가")
        break

# ─── 2. meta 업데이트 ───
old_version = data["meta"]["version"]
old_updated = data["meta"]["lastUpdated"]

data["meta"]["version"] = "2026-05-25"
data["meta"]["lastUpdated"] = "2026-05-25"

# source에 신규 출처 추가
new_sources = [
    "리얼미터(경남일보 의뢰, 경남, 5.21~22)",
    "KBS(한국리서치 의뢰, 울산, 5.21~23)",
    "뉴시스 2026.05.25 판세 보도",
    "머니투데이 2026.05.25 대구 접전 보도"
]
for src in new_sources:
    if src not in data["meta"]["source"]:
        data["meta"]["source"] += f" / {src}"
        changed.append(f"meta.source 추가: {src}")

if old_version != data["meta"]["version"]:
    changed.append(f"meta.version: {old_version} → {data['meta']['version']}")
if old_updated != data["meta"]["lastUpdated"]:
    changed.append(f"meta.lastUpdated: {old_updated} → {data['meta']['lastUpdated']}")

# JSON 저장
with open(CANDIDATES, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("candidates.json 업데이트 완료")
for c in changed:
    print(f"  - {c}")

# ─── 3. index.html 업데이트 ───
with open(INDEX, encoding="utf-8") as f:
    html = f.read()

html_changed = []

# 충남 수치 업데이트: KBS 41.0%:37.0% → 리얼미터(뉴스핌) 43.5%:43.9%
# 대진표 탭 내 충남 카드 (line ~549-562)
# 빅매치 섹션 내 충남 카드 (line ~895-908)
# 상단 dashboard 충남 없음 (충북만 있음)

# 충남 박수현 pct: 41.0% → 43.5%
old_chungnam_dem = 'style="color:#6ea8fe">41.0%</div>\n        </div>\n        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:41.0%">'
new_chungnam_dem = 'style="color:#6ea8fe">43.5%</div>\n        </div>\n        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:43.5%">'

if old_chungnam_dem in html:
    html = html.replace(old_chungnam_dem, new_chungnam_dem)
    html_changed.append("충남 박수현 pct: 41.0% → 43.5% (대진표 탭)")

# 충남 김태흠 pct: 37.0% → 43.9%
old_chungnam_ppu = 'style="color:#ff8080">37.0%</div>\n        </div>\n        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:37.0%">'
new_chungnam_ppu = 'style="color:#ff8080">43.9%</div>\n        </div>\n        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:43.9%">'

if old_chungnam_ppu in html:
    html = html.replace(old_chungnam_ppu, new_chungnam_ppu)
    html_changed.append("충남 김태흠 pct: 37.0% → 43.9% (대진표 탭)")

# 충남 survey date 업데이트 (대진표 탭)
old_chungnam_footer = '2026.05.16~20 · 한국리서치(KBS) — 오차범위 내 접전 +4.0%p'
new_chungnam_footer = '2026.05.18~19 · 리얼미터(뉴스핌 의뢰) — 오차범위 내 초접전 +0.4%p (김태흠 소폭 우세)'
if old_chungnam_footer in html:
    html = html.replace(old_chungnam_footer, new_chungnam_footer)
    html_changed.append("충남 survey date 업데이트 (대진표 탭)")

# 빅매치 섹션 충남 수치 업데이트
# 박수현 41.0% → 43.5%
old_bigmatch_dem = '<div class="candidate-pct" style="color:#6ea8fe">41.0%</div>\n      </div>\n      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:41.0%">'
new_bigmatch_dem = '<div class="candidate-pct" style="color:#6ea8fe">43.5%</div>\n      </div>\n      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-minjoo" style="width:43.5%">'

if old_bigmatch_dem in html:
    html = html.replace(old_bigmatch_dem, new_bigmatch_dem)
    html_changed.append("충남 박수현 pct: 41.0% → 43.5% (빅매치 섹션)")

# 김태흠 37.0% → 43.9%
old_bigmatch_ppu = '<div class="candidate-pct" style="color:#ff8080">37.0%</div>\n      </div>\n      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:37.0%">'
new_bigmatch_ppu = '<div class="candidate-pct" style="color:#ff8080">43.9%</div>\n      </div>\n      <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill bar-gukmin" style="width:43.9%">'

if old_bigmatch_ppu in html:
    html = html.replace(old_bigmatch_ppu, new_bigmatch_ppu)
    html_changed.append("충남 김태흠 pct: 37.0% → 43.9% (빅매치 섹션)")

# 빅매치 섹션 충남 survey date
old_bigmatch_footer = '2026.05.16~20 · 한국리서치(KBS)</span><span style="font-size:11px;color:#6ea8fe;">오차범위 내 접전 +4.0%p</span>'
new_bigmatch_footer = '2026.05.18~19 · 리얼미터(뉴스핌 의뢰)</span><span style="font-size:11px;color:#aaa;">오차범위 내 초접전 +0.4%p (김태흠 소폭 우세)</span>'
if old_bigmatch_footer in html:
    html = html.replace(old_bigmatch_footer, new_bigmatch_footer)
    html_changed.append("충남 빅매치 섹션 survey date 업데이트")

# 상단 dashboard 충북 수치 확인 및 업데이트 (45.9% → 45.4%, 35.7% → 40.8%)
# 이미 45.4%/40.8%로 되어 있는지 확인
if 'style="width:45.9%"' in html and '충청북도' in html:
    # 충북 dashboard 수치 업데이트
    html = html.replace(
        '<div class="item-bar-fill item-bar-minjoo" style="width:45.9%"></div></div>\n                <span class="item-pct" style="color:#6ea8fe">45.9%</span>',
        '<div class="item-bar-fill item-bar-minjoo" style="width:45.4%"></div></div>\n                <span class="item-pct" style="color:#6ea8fe">45.4%</span>'
    )
    html = html.replace(
        '<div class="item-bar-fill item-bar-gukmin" style="width:35.7%"></div></div>\n                <span class="item-pct" style="color:#ff8080">35.7%</span>',
        '<div class="item-bar-fill item-bar-gukmin" style="width:40.8%"></div></div>\n                <span class="item-pct" style="color:#ff8080">40.8%</span>'
    )
    html_changed.append("충북 dashboard 수치: 45.9%/35.7% → 45.4%/40.8%")

# 여론조사 요약 판세 칩 업데이트
# 현재: 민주 우세 8 (압승 1 포함), 국힘 우세 1, 오차범위 내 접전 6
# 변경 없음 (충남이 접전으로 유지되므로)

# 버전 업데이트 (v10 → v11)
if '(v10)' in html:
    html = html.replace('(v10)', '(v11)')
    html_changed.append("버전: v10 → v11")

with open(INDEX, "w", encoding="utf-8") as f:
    f.write(html)

print("\nindex.html 업데이트 완료")
for c in html_changed:
    print(f"  - {c}")

if not html_changed:
    print("  (변경 사항 없음 - 이미 최신 상태)")

print("\n업데이트 완료!")
