#!/usr/bin/env python3
"""
선거 데이터 자동 업데이트 스크립트
- 연합뉴스·뉴시스·동아일보 RSS에서 선거 관련 뉴스 수집
- OpenAI GPT-4.1-mini로 공천 확정 및 여론조사 수치 추출
- candidates.json 자동 업데이트
"""

import json
import os
import re
import sys
import time
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from openai import OpenAI

# ── 설정 ──────────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATES_PATH = os.path.join(BASE_DIR, "data", "candidates.json")

RSS_FEEDS = [
    "https://www.yna.co.kr/rss/politics.xml",       # 연합뉴스 정치
    "https://www.yna.co.kr/rss/local.xml",           # 연합뉴스 지역
    "https://www.yna.co.kr/rss/all.xml",             # 연합뉴스 전체
    "https://www.newsis.com/RSS/politics.xml",       # 뉴시스 정치
    "https://rss.donga.com/politics.xml",            # 동아일보 정치
]

KEYWORDS = [
    "지방선거", "공천", "후보", "여론조사", "광역단체장",
    "시장", "도지사", "구청장", "보궐선거", "2026",
    "단수공천", "전략공천", "공천확정", "공천 확정"
]

# OpenAI API 설정
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))


# ── 뉴스 수집 ─────────────────────────────────────────────────────────────────
def fetch_news() -> list[dict]:
    """RSS 피드에서 선거 관련 뉴스 수집"""
    articles = []
    seen_titles = set()
    headers = {"User-Agent": "Mozilla/5.0 (compatible; election-bot/1.0)"}

    for feed_url in RSS_FEEDS:
        try:
            resp = requests.get(feed_url, headers=headers, timeout=10)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "xml")
            items = soup.find_all("item")[:50]  # 피드당 50건 수집

            for item in items:
                title = item.find("title")
                desc = item.find("description")
                pub_date = item.find("pubDate")

                title_text = title.get_text(strip=True) if title else ""
                desc_text = desc.get_text(strip=True) if desc else ""
                combined = title_text + " " + desc_text

                # 중복 제거
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


# ── OpenAI 분석 ───────────────────────────────────────────────────────────────
def analyze_with_openai(articles: list[dict], candidates_data: dict) -> dict:
    """OpenAI GPT-4.1-mini로 뉴스에서 데이터 변경사항 추출"""

    if not articles:
        print("분석할 기사 없음")
        return {}

    current_summary = []
    for section in ["gwangyeok", "byeol"]:
        for region in candidates_data.get(section, []):
            for cand in region.get("candidates", []):
                current_summary.append({
                    "region": region["region"],
                    "name": cand["name"],
                    "party": cand["partyName"],
                    "status": cand.get("status", ""),
                    "pct": cand.get("pct")
                })

    news_text = "\n".join([
        f"[{a['date']}] {a['title']}\n{a['desc']}"
        for a in articles[:30]
    ])

    prompt = f"""당신은 2026년 한국 지방선거 데이터 분석 전문가입니다.
아래 뉴스 기사들을 분석하여 현재 후보 데이터에서 업데이트가 필요한 항목을 찾아주세요.

## 현재 후보 데이터 (요약)
{json.dumps(current_summary, ensure_ascii=False, indent=2)}

## 최신 뉴스 기사
{news_text}

## 지시사항
1. 뉴스에서 **공식 공천 확정** 또는 **공식 여론조사 수치**만 추출하세요.
2. 반드시 아래 조건을 모두 충족해야 업데이트 항목에 포함하세요:
   - '공천확정', '단수공천', '전략공천', '공천 확정' 등 확정 표현이 명시된 경우만 status 업데이트
   - 구체적인 퍼센트 수치가 기사에 명시된 경우만 pct 업데이트
   - '가능성', '검토', '거론', '출마 의향' 등 불확실한 표현은 절대 포함하지 마세요
3. 현재 데이터에 이미 '공천확정'인 후보는 status를 업데이트하지 마세요.
4. 현재 데이터의 지역명과 정확히 일치하는 경우만 포함하세요.
   - 후보명이 '미확정', '공천 진행 중', '민주 후보', '국힘 후보', '조국혁신당 후보' 등 미정인 경우,
     뉴스에서 해당 지역·정당의 후보가 확정되면 field를 "name"으로 하여 새 이름으로 교체하세요.
   - 이름 교체 시 status도 "공천확정"으로 함께 업데이트하세요 (별도 항목으로 추가).
5. 아래 JSON 형식으로만 응답하세요. 변경사항이 없으면 빈 배열 반환.
   반드시 JSON만 응답하고 마크다운 코드블록(```)은 사용하지 마세요.

응답 형식:
{{
  "updates": [
    {{
      "region": "지역명 (현재 데이터와 정확히 일치)",
      "candidate_name": "현재 데이터의 후보명 (교체 대상이면 현재 미정 이름)",
      "field": "status 또는 pct 또는 name",
      "old_value": "현재 값",
      "new_value": "새 값",
      "reason": "변경 근거 (기사 내용 요약)"
    }}
  ]
}}"""

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "당신은 한국 지방선거 데이터 분석 전문가입니다. 반드시 JSON 형식으로만 응답하세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            raw = response.choices[0].message.content.strip()
            break
        except Exception as e:
            if attempt < 2 and ("429" in str(e) or "rate" in str(e).lower()):
                wait = 30 * (attempt + 1)
                print(f"Rate limit — {wait}초 대기 후 재시도 ({attempt+1}/3)")
                time.sleep(wait)
            else:
                print(f"OpenAI 분석 실패: {e}")
                return {}
    else:
        return {}

    try:
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        updates = result.get("updates", [])
        print(f"OpenAI 분석 완료: {len(updates)}개 업데이트 항목 발견")
        return result
    except Exception as e:
        print(f"JSON 파싱 실패: {e}")
        print(f"원본 응답: {raw[:500]}")
        return {}


# ── candidates.json 업데이트 ──────────────────────────────────────────────────
def apply_updates(candidates_data: dict, updates: list[dict]) -> tuple[dict, int]:
    """추출된 업데이트를 candidates.json에 적용"""
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
                    # 이름 매칭: 정확히 일치하거나 old_value와 일치
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
                            cand["pct"] = float(new_value)
                            region["surveyDate"] = today
                            print(f"  ✓ {region_name} {cand_name}: pct {old} → {new_value} ({reason})")
                            change_count += 1
                            found = True
                        except (ValueError, TypeError):
                            print(f"  ✗ pct 변환 실패: {new_value}")
                    elif field == "name":
                        old = cand.get("name", "")
                        # 미정 후보명인 경우에만 교체 허용
                        undecided = ["미확정", "공천 진행 중", "민주 후보", "국힘 후보",
                                     "조국혁신당 후보", "무소속 후보", "공천 중"]
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
    print(f"{'='*60}\n")

    with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
        candidates_data = json.load(f)

    articles = fetch_news()

    if not articles:
        print("수집된 기사 없음 — 종료")
        sys.exit(0)

    result = analyze_with_openai(articles, candidates_data)
    updates = result.get("updates", [])

    if not updates:
        print("업데이트 항목 없음 — 종료")
        sys.exit(0)

    print("\n[업데이트 적용]")
    updated_data, change_count = apply_updates(candidates_data, updates)

    if change_count == 0:
        print("실제 변경사항 없음 — 종료")
        sys.exit(0)

    with open(CANDIDATES_PATH, "w", encoding="utf-8") as f:
        json.dump(updated_data, f, ensure_ascii=False, indent=2)

    print(f"\n총 {change_count}개 항목 업데이트 완료 → {CANDIDATES_PATH}")


if __name__ == "__main__":
    main()
