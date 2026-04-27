/**
 * polls.js — 2026 지방선거 여론조사 렌더링 엔진
 * 
 * candidates.json 단일 파일을 읽어 index.html 및 17개 광역단체장 상세 페이지를
 * 자동으로 렌더링합니다. 수치 업데이트 시 candidates.json만 수정하면 됩니다.
 *
 * 사용법:
 *   - index.html   : <script src="js/polls.js"></script> 포함 후 자동 실행
 *   - 상세 페이지  : <script src="../../js/polls.js"></script> 포함 후 자동 실행
 *                    <body data-region="seoul"> 속성으로 지역 ID 지정
 */

(function () {
  'use strict';

  // ── JSON 경로 자동 감지 ──────────────────────────────────────────────────
  const isDetail = document.body.hasAttribute('data-region');
  const JSON_PATH = isDetail
    ? '../../data/candidates.json'
    : 'data/candidates.json';

  // ── 유틸 ────────────────────────────────────────────────────────────────
  function pctStr(v) {
    if (v === null || v === undefined) return '—';
    return Number(v).toFixed(1) + '%';
  }

  function gapColor(gap) {
    if (!gap) return '#8b949e';
    if (gap.startsWith('+')) return '#6ea8fe';
    if (gap.startsWith('-')) return '#ff8080';
    return '#c4b5fd';
  }

  // ── 판세 배지 HTML ───────────────────────────────────────────────────────
  function verdictBadge(verdict, verdictLabels) {
    const v = verdictLabels[verdict] || { label: verdict, badgeClass: 'badge-close' };
    return `<span class="verdict-badge ${v.badgeClass}">${v.label}</span>`;
  }

  // ── 정당 색상 클래스 ─────────────────────────────────────────────────────
  function partyTextClass(party) {
    const map = {
      minjoo: '#6ea8fe', gukmin: '#ff8080', joguk: '#7eb3ff',
      gaehyeok: '#fb923c', jeongeui: '#c4b5fd', jinbo: '#fda4af', musosok: '#cbd5e1'
    };
    return map[party] || '#c9d1d9';
  }

  function partyBorderColor(party) {
    const map = {
      minjoo: '#004ea2', gukmin: '#c9151e', joguk: '#003087',
      gaehyeok: '#e85d00', jeongeui: '#6d28d9', jinbo: '#e11d48', musosok: '#64748b'
    };
    return map[party] || '#30363d';
  }

  function partyChartColor(party) {
    const map = {
      minjoo: { border: '#004ea2', bg: 'rgba(0,78,162,0.15)' },
      gukmin: { border: '#c9151e', bg: 'rgba(201,21,30,0.10)' },
      joguk:  { border: '#003087', bg: 'rgba(0,48,135,0.15)' },
      gaehyeok: { border: '#e85d00', bg: 'rgba(232,93,0,0.15)' },
      jeongeui: { border: '#6d28d9', bg: 'rgba(109,40,217,0.15)' },
      jinbo: { border: '#e11d48', bg: 'rgba(225,29,72,0.15)' },
      musosok: { border: '#64748b', bg: 'rgba(100,116,139,0.15)' }
    };
    return map[party] || { border: '#8b949e', bg: 'rgba(139,148,158,0.15)' };
  }

  // ════════════════════════════════════════════════════════════════════════
  // INDEX.HTML 렌더링
  // ════════════════════════════════════════════════════════════════════════
  function renderIndex(data) {
    renderIndexVerdictSummary(data);
    renderIndexSurveyTable(data);
    renderIndexCards(data);
    renderIndexSidebar(data);
  }

  // 판세 요약 칩 (민주 우세 N / 국힘 우세 N / 접전 N)
  function renderIndexVerdictSummary(data) {
    const el = document.getElementById('verdict-summary');
    if (!el) return;

    let minjoo = 0, gukmin = 0, close = 0;
    data.gwangyeok.forEach(r => {
      if (r.verdict === 'minjoo' || r.verdict === 'minjoo_strong') minjoo++;
      else if (r.verdict === 'gukmin') gukmin++;
      else close++;
    });

    el.innerHTML = `
      <span class="verdict-chip chip-minjoo">민주 우세 ${minjoo}</span>
      <span class="verdict-chip chip-gukmin">국힘 우세 ${gukmin}</span>
      <span class="verdict-chip chip-close">접전 ${close}</span>
    `;
  }

  // 여론조사 요약 테이블
  function renderIndexSurveyTable(data) {
    const tbody = document.getElementById('survey-table-body');
    if (!tbody) return;

    tbody.innerHTML = data.gwangyeok.map(r => {
      const c0 = r.candidates[0];
      const c1 = r.candidates[1];
      const latest = r.history && r.history[0];
      const gap = latest ? latest.gap : '—';
      const vl = data.verdict_labels[r.verdict] || { label: r.verdict, badgeClass: 'badge-close' };
      const gapCol = gapColor(gap);

      const p0short = (c0.partyName||'').replace('더불어민주당','민주').replace('국민의힘','국힘').replace('조국혁신당','조국').replace('개혁신당','개혁');
      const p1short = (c1.partyName||'').replace('더불어민주당','민주').replace('국민의힘','국힘').replace('조국혁신당','조국').replace('개혁신당','개혁');
      const textColor0 = partyTextClass(c0.party);
      const textColor1 = partyTextClass(c1.party);
      return `<tr>
        <td class="td-region">${r.region}</td>
        <td class="td-cand1" style="color:${textColor0};cursor:pointer;" onclick="openPollsCandModal('${r.id}',0)"><span style="text-decoration:underline dotted;">${c0.name}</span><span style="font-size:11px;opacity:0.75;margin-left:4px;">(${p0short})</span></td>
        <td class="td-cand1" style="color:${textColor0};">${pctStr(c0.pct)}</td>
        <td class="td-cand2" style="color:${textColor1};cursor:pointer;" onclick="openPollsCandModal('${r.id}',1)"><span style="text-decoration:underline dotted;">${c1.name}</span><span style="font-size:11px;opacity:0.75;margin-left:4px;">(${p1short})</span></td>
        <td class="td-cand2" style="color:${textColor1};">${pctStr(c1.pct)}</td>
        <td class="td-gap" style="color:${gapCol};">${gap}</td>
        <td><span class="verdict-badge ${vl.badgeClass}" style="font-size:11px;padding:3px 8px;">${vl.label}</span></td>
        <td class="td-source">${r.surveyDate}</td>
        <td class="td-source">${r.surveyOrg}</td>
      </tr>`;
    }).join('');
  }

  // 판세 현황판 카드 (광역단체장) - match-card 구조
  function renderIndexCards(data) {
    const container = document.getElementById('gwangyeok-cards');
    if (!container) return;

    container.innerHTML = data.gwangyeok.map(r => {
      const c0 = r.candidates[0];
      const c1 = r.candidates[1];
      const vl = data.verdict_labels[r.verdict] || { label: r.verdict, badgeClass: 'badge-close' };
      const detailUrl = `pages/gwangyeok/${r.id}.html`;
      const pct0 = c0.pct !== null ? c0.pct : 0;
      const pct1 = c1.pct !== null ? c1.pct : 0;
      const textColor0 = partyTextClass(c0.party);
      const textColor1 = partyTextClass(c1.party);
      const barClass0 = c0.party === 'gukmin' ? 'bar-gukmin' : 'bar-minjoo';
      const barClass1 = c1.party === 'gukmin' ? 'bar-gukmin' : 'bar-minjoo';
      const avatarClass0 = c0.party === 'gukmin' ? 'avatar-gukmin' : 'avatar-minjoo';
      const avatarClass1 = c1.party === 'gukmin' ? 'avatar-gukmin' : 'avatar-minjoo';
      const initial0 = c0.name ? c0.name[0] : '?';
      const initial1 = c1.name ? c1.name[0] : '?';
      const partyShort0 = c0.partyName.replace('더불어민주당','민주').replace('국민의힘','국힘').replace('조국혁신당','조국').replace('개혁신당','개혁');
      const partyShort1 = c1.partyName.replace('더불어민주당','민주').replace('국민의힘','국힘').replace('조국혁신당','조국').replace('개혁신당','개혁');

      return `<div class="match-card">
        <div class="region-tag"><span>${r.emoji} ${r.region}</span><span class="verdict-badge ${vl.badgeClass}">${vl.label}</span></div>
        <div class="region-name">${r.title}</div>
        <div class="candidate-row" style="cursor:pointer;" onclick="openPollsCandModal('${r.id}',0)">
          <div class="candidate-avatar ${avatarClass0}">${initial0}</div>
          <div class="candidate-info">
            <div class="candidate-name" style="text-decoration:underline dotted;">${c0.name}</div>
            <div class="candidate-party">${c0.partyName} · ${c0.status}</div>
          </div>
          <div class="candidate-pct" style="color:${textColor0}">${pctStr(c0.pct)}</div>
        </div>
        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill ${barClass0}" style="width:${pct0}%"></div></div></div>
        <div class="candidate-row" style="margin-top:8px;cursor:pointer;" onclick="openPollsCandModal('${r.id}',1)">
          <div class="candidate-avatar ${avatarClass1}">${initial1}</div>
          <div class="candidate-info">
            <div class="candidate-name" style="text-decoration:underline dotted;">${c1.name}</div>
            <div class="candidate-party">${c1.partyName} · ${c1.status}</div>
          </div>
          <div class="candidate-pct" style="color:${textColor1}">${pctStr(c1.pct)}</div>
        </div>
        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill ${barClass1}" style="width:${pct1}%"></div></div></div>
        <div class="match-footer">
          <span class="survey-date">📅 ${r.surveyDate} · ${r.surveyOrg}</span>
          <a href="${detailUrl}" style="font-size:12px;color:#388bfd;font-weight:700;">상세 보기 →</a>
        </div>
      </div>`;
    }).join('');
  }

  // 사이드바 cat-list 렌더링
  function renderIndexSidebar(data) {
    const container = document.getElementById('cat-gwangyeok');
    if (!container) return;

    // 상위 4개 + 전체 보기 링크만 표시
    const top4 = data.gwangyeok.slice(0, 4);
    const items = top4.map(r => {
      const c0 = r.candidates[0];
      const c1 = r.candidates[1];
      const vl = data.verdict_labels[r.verdict] || { label: r.verdict, badgeClass: 'badge-close' };
      const badgeClass = r.verdict === 'gukmin' ? 'badge-n' : r.verdict === 'close' ? 'badge-c' : 'badge-m';
      const badgeLabel = vl.label;
      const pct0 = c0.pct !== null ? c0.pct : 0;
      const pct1 = c1.pct !== null ? c1.pct : 0;
      const textColor0 = partyTextClass(c0.party);
      const textColor1 = partyTextClass(c1.party);
      const barFillClass0 = c0.party === 'gukmin' ? 'item-bar-gukmin' : 'item-bar-minjoo';
      const barFillClass1 = c1.party === 'gukmin' ? 'item-bar-gukmin' : 'item-bar-minjoo';

      return `<a class="cat-item" href="#section-daejinaepyo" onclick="switchTab('tab-gwangyeok','tabGroup1')">
        <div class="item-left">
          <div class="item-region">${r.emoji} ${r.region}</div>
          <div class="item-cands">${c0.name}(민주) vs ${c1.name}(국힘)</div>
        </div>
        <div class="item-bar-wrap">
          <div class="item-bar-row">
            <span class="item-bar-label" style="color:${textColor0}">민</span>
            <div class="item-bar-bg"><div class="item-bar-fill ${barFillClass0}" style="width:${pct0}%"></div></div>
            <span class="item-pct" style="color:${textColor0}">${pctStr(c0.pct)}</span>
          </div>
          <div class="item-bar-row">
            <span class="item-bar-label" style="color:${textColor1}">국</span>
            <div class="item-bar-bg"><div class="item-bar-fill ${barFillClass1}" style="width:${pct1}%"></div></div>
            <span class="item-pct" style="color:${textColor1}">${pctStr(c1.pct)}</span>
          </div>
        </div>
        <span class="item-badge ${badgeClass}">${badgeLabel}</span>
        <span class="item-arrow">›</span>
      </a>`;
    }).join('');

    container.innerHTML = items + `<a class="cat-item" href="#section-daejinaepyo" onclick="switchTab('tab-gwangyeok','tabGroup1')" style="justify-content:center;color:#388bfd;font-size:12px;font-weight:700;">
      전체 ${data.gwangyeok.length}개 지역 보기 →
    </a>`;
  }

  // ════════════════════════════════════════════════════════════════════════
  // 상세 페이지 렌더링
  // ════════════════════════════════════════════════════════════════════════
  function renderDetail(data, regionId) {
    const region = data.gwangyeok.find(r => r.id === regionId);
    if (!region) {
      console.error('[polls.js] 지역 데이터를 찾을 수 없습니다:', regionId);
      return;
    }

    renderDetailHeader(region, data.verdict_labels);
    renderDetailCandidateCards(region);
    renderDetailSurveyTable(region);
    renderDetailChart(region);
    renderDetailLastUpdated(region);
  }

  // 헤더 (지역명 + 판세 배지)
  function renderDetailHeader(region, verdictLabels) {
    const titleEl = document.getElementById('detail-title');
    const badgeEl = document.getElementById('detail-verdict-badge');
    const subtitleEl = document.getElementById('detail-subtitle');

    if (titleEl) titleEl.textContent = `${region.emoji} ${region.region} ${region.title}`;
    if (badgeEl) {
      const vl = verdictLabels[region.verdict] || { label: region.verdict, badgeClass: 'badge-close' };
      badgeEl.className = `verdict-badge ${vl.badgeClass}`;
      badgeEl.textContent = vl.label;
    }
    if (subtitleEl) {
      subtitleEl.textContent = `선거여론조사심의위원회 등록 최신 조사 기준`;
    }
  }

  // 후보 카드 2개
  function renderDetailCandidateCards(region) {
    const container = document.getElementById('detail-candidate-cards');
    if (!container) return;

    container.innerHTML = region.candidates.map(c => {
      const borderColor = partyBorderColor(c.party);
      const textColor = partyTextClass(c.party);
      const barClass = c.party === 'gukmin' ? 'bar-gukmin' : 'bar-minjoo';
      const avatarClass = c.party === 'gukmin' ? 'avatar-gukmin' : 'avatar-minjoo';
      const pctVal = c.pct !== null ? c.pct : 0;
      const initial = c.name ? c.name[0] : '?';

      const candIdx = region.candidates.indexOf(c);
      return `<div class="cand-detail-card" style="border-left:4px solid ${borderColor};">
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:12px;cursor:pointer;" onclick="openPollsCandModal('${region.id}',${candIdx})">
          <div class="candidate-avatar ${avatarClass}" style="width:56px;height:56px;font-size:20px;">${initial}</div>
          <div>
            <div style="font-size:20px;font-weight:900;text-decoration:underline dotted;">${c.name}</div>
            <div style="font-size:12px;color:${textColor};font-weight:700;">${c.partyName} · ${c.status}</div>
          </div>
          <div style="margin-left:auto;font-size:28px;font-weight:900;color:${textColor};">${pctStr(c.pct)}</div>
        </div>
        <div class="bar-wrap"><div class="bar-bg"><div class="bar-fill ${barClass}" style="width:${pctVal}%;height:12px;border-radius:6px;"></div></div></div>
        <table style="width:100%;margin-top:12px;font-size:12px;border-collapse:collapse;">
          <tr><td style="color:#8b949e;padding:3px 0;">나이</td><td style="font-weight:600;">${c.age || '—'}</td></tr>
          <tr><td style="color:#8b949e;padding:3px 0;">현직</td><td style="font-weight:600;">${c.current || '—'}</td></tr>
          <tr><td style="color:#8b949e;padding:3px 0;">학력</td><td style="font-weight:600;">${c.education || '—'}</td></tr>
          <tr><td style="color:#8b949e;padding:3px 0;">주요 경력</td><td style="font-weight:600;">${c.career || '—'}</td></tr>
          <tr><td style="color:#8b949e;padding:3px 0;">핵심 공약</td><td style="font-weight:600;">${c.pledge || '—'}</td></tr>
        </table>
        <a href="https://info.nec.go.kr" target="_blank" class="modal-link" style="margin-top:12px;display:block;font-size:11px;">🔗 선관위 후보자 정보 보기</a>
      </div>`;
    }).join('');
  }

  // 여론조사 히스토리 테이블
  function renderDetailSurveyTable(region) {
    const tbody = document.getElementById('detail-survey-tbody');
    if (!tbody) return;

    // 테이블 헤더 후보명 업데이트
    const th0 = document.getElementById('detail-th-cand0');
    const th1 = document.getElementById('detail-th-cand1');
    if (th0 && region.candidates[0]) th0.textContent = `${region.candidates[0].name}(${region.candidates[0].partyName.replace('더불어민주당','민주').replace('국민의힘','국힘')})`;
    if (th1 && region.candidates[1]) th1.textContent = `${region.candidates[1].name}(${region.candidates[1].partyName.replace('더불어민주당','민주').replace('국민의힘','국힘')})`;

    if (!region.history || region.history.length === 0) {
      tbody.innerHTML = '<tr><td colspan="6" style="text-align:center;color:#8b949e;">조사 결과 없음</td></tr>';
      return;
    }

    tbody.innerHTML = region.history.map(h => {
      const p0 = h.pcts && h.pcts[0] !== undefined ? pctStr(h.pcts[0]) : '—';
      const p1 = h.pcts && h.pcts[1] !== undefined ? pctStr(h.pcts[1]) : '—';
      const gapCol = gapColor(h.gap);
      return `<tr>
        <td class="td-source">${h.date}</td>
        <td class="td-source">${h.org}</td>
        <td class="td-cand1">${p0}</td>
        <td class="td-cand2">${p1}</td>
        <td class="td-gap" style="color:${gapCol};">${h.gap || '—'}</td>
        <td class="td-source">${h.sample || '—'}</td>
      </tr>`;
    }).join('');
  }

  // 여론조사 추이 차트 (Chart.js)
  function renderDetailChart(region) {
    const canvas = document.getElementById('surveyChart');
    if (!canvas || !window.Chart) return;
    if (!region.history || region.history.length === 0) return;

    // 날짜 역순 정렬 (오래된 것 → 최신)
    const sorted = [...region.history].reverse();
    const labels = sorted.map(h => {
      // "2026.04.22~23" → "04.22"
      const m = h.date.match(/\d{4}\.(\d{2}\.\d{2})/);
      return m ? m[1] : h.date;
    });

    const datasets = region.candidates.map(c => {
      const color = partyChartColor(c.party);
      const idx = region.candidates.indexOf(c);
      return {
        label: `${c.name} (${c.partyName.replace('더불어민주당','민주').replace('국민의힘','국힘')})`,
        data: sorted.map(h => h.pcts && h.pcts[idx] !== undefined ? h.pcts[idx] : null),
        borderColor: color.border,
        backgroundColor: color.bg,
        borderWidth: 3,
        pointRadius: 5,
        tension: 0.3,
        fill: true
      };
    });

    // 기존 차트 인스턴스 제거
    if (canvas._chartInstance) {
      canvas._chartInstance.destroy();
    }

    const allPcts = region.history.flatMap(h => h.pcts || []).filter(v => v !== null);
    const minPct = Math.max(0, Math.floor(Math.min(...allPcts) / 10) * 10 - 5);
    const maxPct = Math.min(100, Math.ceil(Math.max(...allPcts) / 10) * 10 + 5);

    canvas._chartInstance = new Chart(canvas.getContext('2d'), {
      type: 'line',
      data: { labels, datasets },
      options: {
        responsive: true,
        plugins: {
          legend: { labels: { color: '#c9d1d9', font: { family: 'Noto Sans KR', size: 12 } } },
          tooltip: { mode: 'index', intersect: false }
        },
        scales: {
          x: { ticks: { color: '#8b949e' }, grid: { color: '#21262d' } },
          y: {
            min: minPct, max: maxPct,
            ticks: { color: '#8b949e', callback: v => v + '%' },
            grid: { color: '#21262d' }
          }
        }
      }
    });
  }

  // 마지막 업데이트 표시
  function renderDetailLastUpdated(region) {
    const el = document.getElementById('detail-last-updated');
    if (!el) return;
    el.textContent = `출처: ${region.surveyOrg} | 최종 업데이트: ${region.surveyDate}`;
  }

  // ════════════════════════════════════════════════════════════════════════
  // 진입점
  // ════════════════════════════════════════════════════════════════════════
  // ════════════════════════════════════════════════════════════════════════
  // 후보 프로필 모달
  // ════════════════════════════════════════════════════════════════════════
  // 모달 HTML이 없으면 자동 삽입 (상세 페이지 등)
  function ensureModal() {
    if (document.getElementById('polls-modal')) return;
    const html = `
    <div class="modal-overlay" id="polls-modal" onclick="if(event.target===this)closePollsModal()">
      <div class="modal-box">
        <button class="modal-close" onclick="closePollsModal()">✕</button>
        <div class="modal-header">
          <div class="modal-avatar" id="pm-avatar">?</div>
          <div>
            <div class="modal-name" id="pm-name">후보자</div>
            <div class="modal-party" id="pm-party"></div>
            <div style="font-size:11px;color:#8b949e;margin-top:2px;" id="pm-region"></div>
          </div>
        </div>
        <div class="modal-section"><h4>나이</h4><p id="pm-age">확인 중</p></div>
        <div class="modal-section"><h4>현직</h4><p id="pm-current">—</p></div>
        <div class="modal-section"><h4>학력</h4><p id="pm-education">—</p></div>
        <div class="modal-section"><h4>주요 경력</h4><p id="pm-career">—</p></div>
        <div class="modal-section"><h4>핵심 공약</h4><p id="pm-pledge">—</p></div>
        <a class="modal-link" id="pm-detail-link" href="#" style="display:none;">📄 상세 페이지 보기 →</a>
        <a class="modal-link" href="https://info.nec.go.kr" target="_blank">🔗 중앙선관위 후보자 정보</a>
      </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', html);
    document.addEventListener('keydown', e => { if (e.key === 'Escape') closePollsModal(); });
  }
  window.closePollsModal = function() {
    const m = document.getElementById('polls-modal');
    if (m) m.classList.remove('show');
  };
  function openPollsModal(c, regionTitle, detailUrl) {
    ensureModal();
    const partyColors = {
      minjoo: { bg: '#004ea2', text: '#6ea8fe', label: '더불어민주당' },
      gukmin: { bg: '#c9151e', text: '#ff8080', label: '국민의힘' },
      joguk:  { bg: '#003087', text: '#7eb3ff', label: '조국혁신당' },
      gaehyeok: { bg: '#e85d00', text: '#fb923c', label: '개혁신당' },
      musosok: { bg: '#475569', text: '#cbd5e1', label: '무소속' }
    };
    const pc = partyColors[c.party] || { bg: '#475569', text: '#cbd5e1', label: c.partyName || '' };
    const av = document.getElementById('pm-avatar');
    av.style.background = pc.bg;
    av.textContent = c.name ? c.name[0] : '?';
    document.getElementById('pm-name').textContent = c.name || '후보자';
    const partyEl = document.getElementById('pm-party');
    partyEl.textContent = pc.label + (c.status ? ' · ' + c.status : '');
    partyEl.style.color = pc.text;
    document.getElementById('pm-region').textContent = regionTitle || '';
    document.getElementById('pm-age').textContent = c.age || '확인 중';
    document.getElementById('pm-current').textContent = c.current || '—';
    document.getElementById('pm-education').textContent = c.education || '—';
    document.getElementById('pm-career').textContent = c.career || '—';
    document.getElementById('pm-pledge').textContent = c.pledge || '—';
    const detailLink = document.getElementById('pm-detail-link');
    if (detailUrl) {
      detailLink.href = detailUrl;
      detailLink.style.display = 'block';
    } else {
      detailLink.style.display = 'none';
    }
    document.getElementById('polls-modal').classList.add('show');
  }
  // 전역 노출 (index.html의 기존 onclick에서도 호출 가능)
  window._pollsData = null;
  window.openPollsCandModal = function(regionId, candIdx) {
    if (!window._pollsData) return;
    const region = window._pollsData.gwangyeok.find(r => r.id === regionId);
    if (!region) return;
    const c = region.candidates[candIdx];
    if (!c) return;
    const isDetail = document.body.hasAttribute('data-region');
    const detailUrl = isDetail ? null : `pages/gwangyeok/${regionId}.html`;
    openPollsModal(c, region.title, detailUrl);
  };

  fetch(JSON_PATH)
    .then(r => {
      if (!r.ok) throw new Error('candidates.json 로드 실패: ' + r.status);
      return r.json();
    })
    .then(data => {
      window._pollsData = data;
      if (isDetail) {
        const regionId = document.body.getAttribute('data-region');
        renderDetail(data, regionId);
      } else {
        renderIndex(data);
      }
    })
    .catch(err => {
      console.error('[polls.js] 오류:', err);
    });

})();
