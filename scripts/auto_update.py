#!/usr/bin/env python3
"""
선거 데이터 자동 업데이트 스크립트 (Gemini 유료 버전)
- 연합뉴스·뉴시스·동아일보·한겨레·조선일보 RSS에서 선거 관련 뉴스 수집
- Google Gemini 2.0 Flash로 공천 확정 및 여론조사 수치 추출
- candidates.json 자동 업데이트 (광역단체장 + 보궐선거 전체)
"""
import json
import os
import re
import sys
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import google.generativeai as genai

# ── 설정 ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "candidates.json")

RSS_FEEDS = [
    "https://www.yna.co.kr/rss/politics.xml",
    "https://www.yna.co.kr/rss/local.xml",
    "https://www.yna.co.kr/rss/all.xml",
    "https://www.newsis.com/RSS/politics.xml",
    "https://rss.donga.com/politics.xml",
    "https://www.hani.co.kr/rss/politics/",
    "https://www.chosun.com/arc/outboundfeeds/rss/category/politics/",
]

KEYWORDS = [
    "지방선거", "공천", "후보", "여론조사", "광역단체장",
    "시장", "도지사", "구청장", "보궐선거", "2026",
    "단수공천", "전략공천", "공천확정", "공천 확정",
    "출마", "선거운동", "지지율", "지지도", "접전", "격전",
    "민주당", "국민의힘", "조국혁신당", "개혁신당"
]

# Gemini API 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("오류: GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")


# ── 뉴스 수집 ─────────────────────────────────────────────────────────────────
def fetch_news() -> list[dict]:
    articles = []
    seen_titles = set()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; election-bot/1.0)"}

    for feed_url in RSS_FEEDS:
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")[:50]

            for item in items:
                title = item.find("title")
                desc = item.find("description")
                pub_date = item.find("pubDate")

                title_text = title.get_text(strip=True) if title else ""
                desc_text = desc.get_text(strip=True) if desc else ""
                combined = title_text + " " + desc_text

                if title_text in seen_titles:
                    continue

                if any(kw in combined for kw in KEYWORDS):
                    articles.append({
                        "title": title_text,
                        "desc": desc_text[:300],
                        "date": pub_date.get_text(strip=True) if pub_date else ""
                    })
                    seen_titles.add(title_text)

        except Exception as e:
            print(f"RSS 수집 실패 ({feed_url}): {e}")

    print(f"수집된 선거 관련 기사: {len(articles)}건")
    return articles


# ── Gemini 분석 ───────────────────────────────────────────────────────────────
def analyze_with_gemini(articles: list[dict], candidates_data: dict) -> dict:
    if not articles:
        print("분석할 기사 없음")
        return {}

    current_summary = []
    for section in ["gwangyeok", "byeol"]:
        for region in candidates_data.get(section, []):
            for cand in region.get("candidates", []):
                current_summary.append({
                    "region": region["region"],
                    "section": section,
                    "name": cand["name"],
                    "party": cand["partyName"],
                    "status": cand.get("status", ""),
                    "pct": cand.get("pct")
                })

    articles_text = "\n\n".join([
        f"[{i+1}] {a['title']}\n{a['desc']}"
        for i, a in enumerate(articles[:80])
    ])

    prompt = f"""당신은 2026년 대한민국 지방선거 데이터 분석 전문가입니다.

아래 뉴스 기사들을 분석하여 후보자 정보 변경사항을 JSON으로 추출해 주세요.

## 현재 등록된 후보 목록 (광역단체장 + 보궐선거 전체):
{json.dumps(current_summary, ensure_ascii=False, indent=2)}

## 최신 뉴스 기사:
{articles_text}

## 추출 규칙:
1. **공천 확정**: status를 "confirmed"로 변경 (단수공천, 전략공천, 공천확정 등)
2. **후보 사퇴/탈락**: status를 "withdrawn"으로 변경
3. **여론조사 수치**: pct 필드를 최신 지지율(%)로 업데이트
4. **후보명 변경**: 미확정 후보명이 실제 이름으로 확정된 경우
5. 광역단체장(gwangyeok)과 보궐선거(byeol) 모두 포함하여 분석
6. 확실한 근거가 있는 경우에만 업데이트 (추측 금지)
7. 이미 현재 값과 동일한 경우 제외

## 응답 형식 (JSON만 출력):
{{
  "updates": [
    {{
      "region": "지역명",
      "candidate_name": "후보자 이름",
      "field": "status 또는 pct 또는 name",
      "old_value": "현재 값",
      "new_value": "새 값",
      "reason": "변경 근거"
    }}
  ]
}}

변경사항이 없으면: {{"updates": []}}"""

    for attempt in range(3):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=4096,
                )
            )
            raw = response.text.strip()
            break
        except Exception as e:
            if attempt < 2 and ("429" in str(e) or "quota" in str(e).lower() or "rate" in str(e).lower()):
                wait = 30 * (attempt + 1)
                print(f"Rate limit — {wait}초 대기 후 재시도 ({attempt+1}/3)")
                time.sleep(wait)
            else:
                print(f"Gemini 분석 실패: {e}")
                return {}
    else:
        return {}

    try:
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        updates = result.get("updates", [])
        print(f"Gemini 분석 완료: {len(updates)}개 업데이트 항목 발견")
        return result
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        print(f"원본 응답: {raw[:500]}")
        return {}


# ── candidates.json 업데이트 ──────────────────────────────────────────────────
def apply_updates(candidates_data: dict, updates: list[dict]) -> tuple[dict, int]:
    change_count = 0
    today = datetime.now().strftime("%Y.%m.%d")

    for update in updates:
        region_name = update.get("region", "")
        cand_name = update.get("candidate_name", "")
        field = update.get("field", "")
        new_value = update.get("new_value")
        reason = update.get("reason", "")

        found = False
        for section in ["gwangyeok", "byeol"]:
            for region in candidates_data.get(section, []):
                if region["region"] != region_name:
                    continue
                for cand in region.get("candidates", []):
                    if cand["name"] != cand_name and update.get("old_value") != cand["name"]:
                        continue

                    if field == "status":
                        old = cand.get("status", "")
                        if old == new_value:
                            print(f"  - {region_name} {cand_name}: status 이미 '{old}' — 스킵")
                            found = True
                            continue
                        cand["status"] = new_value
                        region["surveyDate"] = today
                        print(f"  ✓ {region_name} {cand_name}: status '{old}' → '{new_value}' ({reason})")
                        change_count += 1
                        found = True

                    elif field == "pct":
                        try:
                            old = cand.get("pct")
                            new_pct = float(new_value)
                            if old == new_pct:
                                print(f"  - {region_name} {cand_name}: pct 이미 {old} — 스킵")
                                found = True
                                continue
                            cand["pct"] = new_pct
                            region["surveyDate"] = today
                            print(f"  ✓ {region_name} {cand_name}: pct {old} → {new_pct} ({reason})")
                            change_count += 1
                            found = True
                        except (ValueError, TypeError):
                            print(f"  ✗ pct 변환 실패: {new_value}")

                    elif field == "name":
                        old = cand.get("name", "")
                        undecided = ["미확정", "공천 진행 중", "민주 후보", "국힘 후보",
                                     "조국혁신당 후보", "무소속 후보", "공천 중", "개혁신당 후보"]
                        if any(u in old for u in undecided):
                            cand["name"] = new_value
                            region["surveyDate"] = today
                            print(f"  ✓ {region_name}: 후보명 '{old}' → '{new_value}' ({reason})")
                            change_count += 1
                            found = True
                        else:
                            print(f"  - {region_name}: '{old}'은 이미 확정된 이름 — 교체 스킵")
                            found = True
                    break
                if found:
                    break

        if not found:
            print(f"  ✗ 매칭 실패: {region_name} / {cand_name}")

    return candidates_data, change_count


# ── 메인 ──────────────────────────────────────────────────────────────────────
def main():
    print(f"\n{'='*60}")
    print(f"선거 데이터 자동 업데이트 시작: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"AI 엔진: Google Gemini 2.0 Flash (유료 Tier 1)")
    print(f"{'='*60}\n")

    with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
        candidates_data = json.load(f)

    total_gwangyeok = sum(len(r.get("candidates", [])) for r in candidates_data.get("gwangyeok", []))
    total_byeol = sum(len(r.get("candidates", [])) for r in candidates_data.get("byeol", []))
    print(f"분석 대상: 광역단체장 {total_gwangyeok}명, 보궐선거 {total_byeol}명 (총 {total_gwangyeok + total_byeol}명)\n")

    articles = fetch_news()
    if not articles:
        print("수집된 기사 없음 — 종료")
        sys.exit(0)

    result = analyze_with_gemini(articles, candidates_data)
    updates = result.get("updates", [])

    if not updates:
        print("업데이트 항목 없음 — 종료")
        sys.exit(0)

    print(f"\n[업데이트 적용] {len(updates)}개 항목 처리 중...")
    updated_data, change_count = apply_updates(candidates_data, updates)

    if change_count == 0:
        print("실제 변경사항 없음 — 종료")
        sys.exit(0)

    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"\n총 {change_count}개 항목 업데이트 완료 → {CANDIDATES_PATH}")


if __name__ == "__main__":
    main()
