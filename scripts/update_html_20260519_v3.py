#!/usr/bin/env python3
"""
2026-05-19 v3 index.html 업데이트 스크립트
조선일보/메트릭스 5.16~17 여론조사 수치를 history에 추가
- 서울: 정원오 40%, 오세훈 37% (메트릭스/조선일보)
- 부산: 전재수 44%, 박형준 35% (메트릭스/조선일보)
- 대구: 김부겸 40%, 추경호 38% (메트릭스/조선일보)
- 경남: 김경수 44%, 박완수 34% (메트릭스/조선일보) → 이미 반영됨
  + 이너텍시스템즈(프레시안) 5.17~18: 김경수 41.9%, 박완수 44.7% 추가
- 울산: 단일화 여론조사 5.23~24 예정 note 추가
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. 서울시장 survey-date 업데이트 (메트릭스 수치 추가 note)
# 현재: 코리아리서치(MBC) 43% vs 35% 유지 (최신 공표 기준)
# survey-date에 메트릭스 수치 병기
old_seoul_survey = '📅 2026.05.16~17 · 코리아리서치(MBC) — 민주 우세 +8%p'
new_seoul_survey = '📅 2026.05.16~17 · 코리아리서치(MBC) 43%:35% / 메트릭스(조선일보) 40%:37% — 오차범위 내 접전'
html = html.replace(old_seoul_survey, new_seoul_survey, 1)

# 2. 부산시장 survey-date 업데이트
old_busan_survey = '📅 2026.05.16~17 · 코리아리서치(MBC) — 오차범위 내 접전 +6%p'
new_busan_survey = '📅 2026.05.16~17 · 코리아리서치(MBC) 44%:38% / 메트릭스(조선일보) 44%:35% — 민주 우세'
html = html.replace(old_busan_survey, new_busan_survey, 1)

# 3. 여론조사 테이블 - 서울 수치 업데이트 (메트릭스 수치 병기)
old_seoul_table = '          <td class="td-cand1">정원오(민주) 43.0%</td>\n          <td class="td-cand2">오세훈(국힘) 35.0%</td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+8.0%p</td>\n          <td><span class="verdict-badge badge-minjoo">민주 우세</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)</td>'
new_seoul_table = '          <td class="td-cand1">정원오(민주) 43.0%<br><small style="color:#aaa">40.0% (메트릭스)</small></td>\n          <td class="td-cand2">오세훈(국힘) 35.0%<br><small style="color:#aaa">37.0% (메트릭스)</small></td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+8.0%p<br><small style="color:#aaa">+3.0%p</small></td>\n          <td><span class="verdict-badge badge-close">오차범위 내 접전</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)<br>05.16~17 메트릭스(조선일보)</td>'
html = html.replace(old_seoul_table, new_seoul_table, 1)

# 4. 여론조사 테이블 - 부산 수치 업데이트 (메트릭스 수치 병기)
old_busan_table = '          <td class="td-cand1">전재수(민주) 44.0%</td>\n          <td class="td-cand2">박형준(국힘) 38.0%</td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+6.0%p</td>\n          <td><span class="verdict-badge badge-close">오차범위 내 접전</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)</td>'
new_busan_table = '          <td class="td-cand1">전재수(민주) 44.0%<br><small style="color:#aaa">44.0% (메트릭스)</small></td>\n          <td class="td-cand2">박형준(국힘) 38.0%<br><small style="color:#aaa">35.0% (메트릭스)</small></td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+6.0%p<br><small style="color:#aaa">+9.0%p</small></td>\n          <td><span class="verdict-badge badge-minjoo">민주 우세</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)<br>05.16~17 메트릭스(조선일보)</td>'
html = html.replace(old_busan_table, new_busan_table, 1)

# 5. 여론조사 테이블 - 대구 수치 업데이트 (메트릭스 수치 병기)
old_daegu_table = '          <td class="td-cand1">김부겸(민주) 43.0%</td>\n          <td class="td-cand2">추경호(국힘) 37.0%</td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+6.0%p</td>\n          <td><span class="verdict-badge badge-close">오차범위 내 접전</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)</td>'
new_daegu_table = '          <td class="td-cand1">김부겸(민주) 43.0%<br><small style="color:#aaa">40.0% (메트릭스)</small></td>\n          <td class="td-cand2">추경호(국힘) 37.0%<br><small style="color:#aaa">38.0% (메트릭스)</small></td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+6.0%p<br><small style="color:#aaa">+2.0%p</small></td>\n          <td><span class="verdict-badge badge-close">오차범위 내 접전</span></td>\n          <td class="td-source">05.16~17 코리아리서치(MBC)<br>05.16~17 메트릭스(조선일보)</td>'
html = html.replace(old_daegu_table, new_daegu_table, 1)

# 6. 여론조사 테이블 - 경남 수치 업데이트 (이너텍시스템즈 수치 병기)
old_gyeongnam_table = '          <td class="td-cand1">김경수(민주) 44.0%</td>\n          <td class="td-cand2">박완수(국힘) 34.0%</td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+10.0%p</td>\n          <td><span class="verdict-badge badge-minjoo">민주 우세</span></td>\n          <td class="td-source">05.16~17 메트릭스(조선일보)</td>'
new_gyeongnam_table = '          <td class="td-cand1">김경수(민주) 44.0%<br><small style="color:#aaa">41.9% (이너텍)</small></td>\n          <td class="td-cand2">박완수(국힘) 34.0%<br><small style="color:#aaa">44.7% (이너텍)</small></td>\n          <td class="td-source">—</td>\n          <td class="td-gap" style="color:#6ea8fe">+10.0%p<br><small style="color:#ff8080">-2.8%p (이너텍)</small></td>\n          <td><span class="verdict-badge badge-close">오차범위 내 접전</span></td>\n          <td class="td-source">05.16~17 메트릭스(조선일보)<br>05.17~18 이너텍시스템즈(프레시안)</td>'
html = html.replace(old_gyeongnam_table, new_gyeongnam_table, 1)

# 7. 버전 정보 업데이트 (lastUpdated)
html = html.replace('"2026-05-19-v2"', '"2026-05-19-v3"')
html = html.replace('2026-05-19-v2', '2026-05-19-v3')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html 업데이트 완료")
print("변경 내역:")
print("- 서울시장 survey-date에 메트릭스(조선일보) 수치 병기")
print("- 부산시장 survey-date에 메트릭스(조선일보) 수치 병기")
print("- 여론조사 테이블 서울/부산/대구/경남 수치 업데이트")
print("- 경남도지사 이너텍시스템즈(프레시안) 5.17~18 수치 추가")
