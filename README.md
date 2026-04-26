# 🗳️ 2026 지방선거 정보 허브

> **6.3 전국동시지방선거** 대진표 · 여론조사 · 투표소 찾기 종합 정보 사이트

## 📁 사이트 구조

```
election2026/
├── index.html                  # 메인 페이지
├── css/
│   └── style.css               # 공통 스타일 (정당 색상 체계 포함)
├── js/
│   └── main.js                 # 공통 JavaScript (D-day, 탭, 모달, 공유)
├── data/
│   └── candidates.json         # 후보자 데이터 (GitHub Actions로 자동 업데이트)
└── pages/
    ├── voting.html             # 투표소 찾기 전용 페이지
    ├── gwangyeok/              # 광역단체장 상세 페이지 (16개)
    │   ├── seoul.html
    │   ├── busan.html
    │   └── ... (14개 추가)
    ├── seoul_gu/               # 서울 구청장 상세 페이지 (25개)
    │   ├── gangnam.html
    │   ├── seocho.html
    │   └── ... (23개 추가)
    └── byeol/                  # 국회의원 보궐선거 상세 페이지 (8개)
        ├── incheon_gyeyang.html
        ├── gyeonggi_pyeongtaek.html
        └── ... (6개 추가)
```

## 🚀 GitHub Pages 배포 방법

### 1단계: GitHub 저장소 생성
```bash
git init
git add .
git commit -m "feat: 2026 지방선거 정보 허브 초기 배포"
git remote add origin https://github.com/{USERNAME}/election2026.git
git push -u origin main
```

### 2단계: GitHub Pages 활성화
1. GitHub 저장소 → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** / **/ (root)**
4. **Save** 클릭

### 3단계: 도메인 설정 (선택)
- 커스텀 도메인 사용 시 `CNAME` 파일에 도메인 입력
- 예: `election2026.kr`

## 🔄 데이터 업데이트 방법

### 수동 업데이트 (여론조사, 공천 결과)
`data/candidates.json` 파일의 해당 후보 수치를 수정 후 `git push`

### 자동 업데이트 (선관위 API)
`.github/workflows/update-data.yml` 워크플로우가 매일 자정 자동 실행

## 📊 정당 색상 체계

| 정당 | CSS 변수 | 색상 코드 |
|------|----------|-----------|
| 더불어민주당 | `--minjoo` | `#004ea2` |
| 국민의힘 | `--gukmin` | `#c9151e` |
| 조국혁신당 | `--joguk` | `#003087` |
| 개혁신당 | `--gaehyeok` | `#e85d00` |
| 무소속 | `--musosok` | `#64748b` |

## ⚖️ 법적 고지

본 사이트는 **공직선거법 제82조의4**에 따라 선거운동을 목적으로 하지 않으며,
공개된 정보(선관위, 여론조사심의위원회 등록 자료)를 정리·제공하는 정보 허브입니다.

- 후보명: 언론 보도 공천 확정 기준 (연합뉴스·뉴시스 2026.04.26 기준)
- 여론조사 수치: 선거여론조사심의위원회 등록 최신 조사 기준
- 개표 후(2026.06.03 오후 8시~): 실제 득표율로 전환

## 📞 문의

데이터 오류 제보: GitHub Issues 활용
