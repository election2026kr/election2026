/* =============================================
   2026 지방선거 정보 허브 — 공통 JavaScript
   ============================================= */

// ===== D-DAY 계산 =====
function updateDday() {
  const election = new Date('2026-06-03T06:00:00+09:00');
  const now = new Date();
  const diff = election - now;
  if (diff <= 0) {
    document.querySelectorAll('.dday').forEach(el => el.textContent = 'D-Day!');
    document.querySelectorAll('#headerDday').forEach(el => el.textContent = '개표 중');
    return;
  }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  document.querySelectorAll('.dday, #headerDday').forEach(el => {
    el.textContent = `D-${days}`;
  });
}
updateDday();
setInterval(updateDday, 60000);

// ===== 탭 전환 =====
function switchTab(tabId, groupId) {
  const group = document.getElementById(groupId) || document;
  group.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  group.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  const activeBtn = group.querySelector(`[data-tab="${tabId}"]`);
  const activeContent = document.getElementById(tabId);
  if (activeBtn) activeBtn.classList.add('active');
  if (activeContent) activeContent.classList.add('active');
}

// 탭 버튼 이벤트 등록
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const tabId = btn.dataset.tab;
      const groupId = btn.dataset.group;
      switchTab(tabId, groupId);
    });
  });
  // 첫 번째 탭 기본 활성화
  document.querySelectorAll('.tab-bar').forEach(bar => {
    const firstBtn = bar.querySelector('.tab-btn');
    if (firstBtn) {
      const tabId = firstBtn.dataset.tab;
      const groupId = firstBtn.dataset.group;
      switchTab(tabId, groupId);
    }
  });
});

// ===== 카테고리 패널 토글 =====
function toggleCat(listId, toggleEl) {
  const list = document.getElementById(listId);
  if (!list) return;
  const isOpen = list.classList.toggle('open');
  if (toggleEl) {
    const toggle = toggleEl.querySelector('.cat-toggle');
    if (toggle) toggle.classList.toggle('open', isOpen);
  }
}

// ===== 후보자 프로필 모달 =====
const PARTY_COLORS = {
  minjoo: { bg: '#004ea2', text: '#6ea8fe', label: '더불어민주당' },
  gukmin: { bg: '#c9151e', text: '#ff8080', label: '국민의힘' },
  joguk:  { bg: '#003087', text: '#7eb3ff', label: '조국혁신당' },
  gaehyeok: { bg: '#e85d00', text: '#fb923c', label: '개혁신당' },
  indep:  { bg: '#64748b', text: '#cbd5e1', label: '무소속' }
};

function openCandModal(name, party, age, career, region, assets, criminal, pledges) {
  const modal = document.getElementById('modal');
  if (!modal) return;
  const color = PARTY_COLORS[party] || PARTY_COLORS['indep'];
  const initial = name ? name[0] : '?';

  document.getElementById('modal-avatar').style.background = color.bg;
  document.getElementById('modal-avatar').textContent = initial;
  document.getElementById('modal-name').textContent = name || '후보 정보';
  document.getElementById('modal-party-label').textContent = color.label;
  document.getElementById('modal-party-label').style.color = color.text;
  document.getElementById('modal-region').textContent = region || '';
  document.getElementById('modal-age').textContent = age || '확인 중';
  document.getElementById('modal-career').textContent = career || '공천 확정 후 업데이트 예정';
  document.getElementById('modal-assets').textContent = assets || '선관위 등록 후 공개';
  document.getElementById('modal-criminal').textContent = criminal || '없음 (선관위 등록 후 확인)';
  document.getElementById('modal-pledges').textContent = pledges || '공천 확정 후 업데이트 예정';

  // 선관위 링크
  const nec = document.getElementById('modal-nec-link');
  if (nec) nec.href = `https://info.nec.go.kr/candidate/candidateList.xhtml`;

  modal.classList.add('show');
}

function closeModal() {
  const modal = document.getElementById('modal');
  if (modal) modal.classList.remove('show');
}

document.addEventListener('click', e => {
  const modal = document.getElementById('modal');
  if (modal && e.target === modal) closeModal();
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});

// ===== 스크롤 이벤트 =====
const NAV_SECTIONS = [
  'section-voting',
  'section-daejinaepyo',
  'section-bigmatch',
  'section-survey',
  'section-guide'
];

window.addEventListener('scroll', () => {
  // 플로팅 버튼
  const floatBtn = document.getElementById('floatTop');
  if (floatBtn) floatBtn.classList.toggle('show', window.scrollY > 400);

  // 활성 네비 하이라이트
  let current = '';
  NAV_SECTIONS.forEach(id => {
    const el = document.getElementById(id);
    if (el && window.scrollY >= el.offsetTop - 110) current = '#' + id;
  });
  document.querySelectorAll('.sticky-nav a').forEach(a => {
    a.classList.remove('nav-active');
    if (a.getAttribute('href') === current) a.classList.add('nav-active');
  });
});

// ===== 맨 위로 =====
function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== 카카오톡 공유 (카카오링크 URL 방식 - 도메인 등록 불필요) =====
function shareKakao() {
  const url = window.location.href;
  // 카카오링크 URL 방식: SDK 초기화/도메인 등록 없이 작동
  const kakaoShareUrl = 'https://sharer.kakao.com/talk/friends/picker/easylink'
    + '?app_key=73d821e57b593140fbd807a993463884'
    + '&lang=ko'
    + '&url=' + encodeURIComponent(url);
  const popup = window.open(kakaoShareUrl, 'kakaoShare', 'width=500,height=600,scrollbars=yes,resizable=yes');
  if (!popup || popup.closed || typeof popup.closed === 'undefined') {
    // 팝업 차단된 경우 링크 복사로 대체
    copyLink();
  }
}

// ===== 링크 복사 =====
function copyLink() {
  navigator.clipboard.writeText(window.location.href).then(() => {
    showToast('링크가 복사되었습니다!');
  }).catch(() => {
    prompt('아래 링크를 복사하세요:', window.location.href);
  });
}

// ===== 토스트 알림 =====
function showToast(msg) {
  let toast = document.getElementById('toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'toast';
    toast.style.cssText = `
      position:fixed; bottom:80px; left:50%; transform:translateX(-50%);
      background:#238636; color:#fff; padding:10px 20px; border-radius:8px;
      font-size:13px; font-weight:700; z-index:999; opacity:0;
      transition:opacity 0.3s;
    `;
    document.body.appendChild(toast);
  }
  toast.textContent = msg;
  toast.style.opacity = '1';
  setTimeout(() => { toast.style.opacity = '0'; }, 2500);
}

// ===== 투표소 찾기 탭 전환 =====
function switchVotingTab(type) {
  document.querySelectorAll('.vtab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.vtype === type);
  });
  document.querySelectorAll('.voting-type-content').forEach(el => {
    el.style.display = el.dataset.vtype === type ? 'block' : 'none';
  });
}

// ===== 투표소 검색 (선관위 API 연동 예정) =====
function searchVoting() {
  const sido = document.getElementById('sido-select')?.value;
  const sigungu = document.getElementById('sigungu-select')?.value;
  const dong = document.getElementById('dong-select')?.value;
  const resultDiv = document.getElementById('voting-result');
  if (!resultDiv) return;

  if (!sido || sido === '') {
    showToast('시·도를 선택해 주세요.');
    return;
  }

  // 실제 배포 시 선관위 OpenAPI 연동
  resultDiv.innerHTML = `
    <div class="voting-card">
      <div class="v-name">📍 ${dong || sigungu || sido} 제1투표소</div>
      <div class="v-addr">주소: 선관위 API 연동 후 실제 주소 표시 예정</div>
      <div style="font-size:11px;color:#8b949e;margin-bottom:8px">⏰ 투표 시간: 오전 6시 ~ 오후 6시</div>
      <button class="btn-map" onclick="window.open('https://map.kakao.com/link/search/${encodeURIComponent((dong || sigungu || sido) + ' 투표소')}')">🗺️ 지도 보기</button>
    </div>
    <div class="notice-box" style="margin-top:12px">
      ⚠️ 현재 선관위 투표소 정보 API 연동 준비 중입니다. 정확한 투표소는
      <a href="https://www.nec.go.kr" target="_blank" style="color:#388bfd">중앙선관위 공식 사이트</a>에서 확인하세요.
    </div>
  `;
}

// ===== 시도 선택 시 시군구 옵션 업데이트 =====
const SIGUNGU_DATA = {
  '서울특별시': ['종로구','중구','용산구','성동구','광진구','동대문구','중랑구','성북구','강북구','도봉구','노원구','은평구','서대문구','마포구','양천구','강서구','구로구','금천구','영등포구','동작구','관악구','서초구','강남구','송파구','강동구'],
  '부산광역시': ['중구','서구','동구','영도구','부산진구','동래구','남구','북구','해운대구','사하구','금정구','강서구','연제구','수영구','사상구','기장군'],
  '대구광역시': ['중구','동구','서구','남구','북구','수성구','달서구','달성군','군위군'],
  '인천광역시': ['중구','동구','미추홀구','연수구','남동구','부평구','계양구','서구','강화군','옹진군'],
  '광주광역시': ['동구','서구','남구','북구','광산구'],
  '대전광역시': ['동구','중구','서구','유성구','대덕구'],
  '울산광역시': ['중구','남구','동구','북구','울주군'],
  '세종특별자치시': ['세종시'],
  '경기도': ['수원시','성남시','의정부시','안양시','부천시','광명시','평택시','동두천시','안산시','고양시','과천시','구리시','남양주시','오산시','시흥시','군포시','의왕시','하남시','용인시','파주시','이천시','안성시','김포시','화성시','광주시','양주시','포천시','여주시','연천군','가평군','양평군'],
  '강원특별자치도': ['춘천시','원주시','강릉시','동해시','태백시','속초시','삼척시','홍천군','횡성군','영월군','평창군','정선군','철원군','화천군','양구군','인제군','고성군','양양군'],
  '충청북도': ['청주시','충주시','제천시','보은군','옥천군','영동군','증평군','진천군','괴산군','음성군','단양군'],
  '충청남도': ['천안시','공주시','보령시','아산시','서산시','논산시','계룡시','당진시','금산군','부여군','서천군','청양군','홍성군','예산군','태안군'],
  '전북특별자치도': ['전주시','군산시','익산시','정읍시','남원시','김제시','완주군','진안군','무주군','장수군','임실군','순창군','고창군','부안군'],
  '전라남도': ['목포시','여수시','순천시','나주시','광양시','담양군','곡성군','구례군','고흥군','보성군','화순군','장흥군','강진군','해남군','영암군','무안군','함평군','영광군','장성군','완도군','진도군','신안군'],
  '경상북도': ['포항시','경주시','김천시','안동시','구미시','영주시','영천시','상주시','문경시','경산시','의성군','청송군','영양군','영덕군','청도군','고령군','성주군','칠곡군','예천군','봉화군','울진군','울릉군'],
  '경상남도': ['창원시','진주시','통영시','사천시','김해시','밀양시','거제시','양산시','의령군','함안군','창녕군','고성군','남해군','하동군','산청군','함양군','거창군','합천군'],
  '제주특별자치도': ['제주시','서귀포시']
};

function updateSigungu() {
  const sido = document.getElementById('sido-select')?.value;
  const sigunguSelect = document.getElementById('sigungu-select');
  if (!sigunguSelect) return;
  sigunguSelect.innerHTML = '<option value="">구·시·군 선택</option>';
  if (sido && SIGUNGU_DATA[sido]) {
    SIGUNGU_DATA[sido].forEach(sg => {
      const opt = document.createElement('option');
      opt.value = sg; opt.textContent = sg;
      sigunguSelect.appendChild(opt);
    });
  }
  // 동 초기화
  const dongSelect = document.getElementById('dong-select');
  if (dongSelect) dongSelect.innerHTML = '<option value="">읍·면·동 선택</option>';
}
