/**
 * PromptShield X — Dashboard Logic
 * Fetches log data, computes stats, renders UI, and manages interactive details.
 */

document.addEventListener('DOMContentLoaded', () => {
  const refreshBtn = document.getElementById('refresh-btn');
  const tableBody = document.getElementById('logs-table-body');
  const logsCount = document.getElementById('logs-count');
  
  // Stat elements
  const statTotal = document.getElementById('stat-total');
  const statPass = document.getElementById('stat-pass');
  const statRewrite = document.getElementById('stat-rewrite');
  const statBlock = document.getElementById('stat-block');

  // Modal elements
  const modalOverlay = document.getElementById('modal-overlay');
  const modalTitle = document.getElementById('modal-title');
  const modalText = document.getElementById('modal-text');
  const modalClose = document.getElementById('modal-close');

  // Open modal helper
  const openModal = (title, text) => {
    modalTitle.textContent = title;
    modalText.textContent = text;
    modalOverlay.classList.add('active');
  };

  // Close modal helper
  const closeModal = () => {
    modalOverlay.classList.remove('active');
  };

  modalClose.addEventListener('click', closeModal);
  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) closeModal();
  });

  // Fetch and render data
  const loadDashboardData = async () => {
    refreshBtn.classList.add('spinning');
    
    try {
      // Fetch logs limit=100 so we can compute stats over a larger history, 
      // but we will only display the last 20 rows.
      const response = await fetch('/admin/logs?limit=100');
      const data = await response.json();
      
      if (data.status === 'ok') {
        const logs = data.logs || [];
        updateStats(logs);
        renderTable(logs.slice(0, 20)); // display only the last 20 rows
      } else {
        showError('API response status not OK');
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      showError('Failed to fetch audit logs.');
    } finally {
      setTimeout(() => {
        refreshBtn.classList.remove('spinning');
      }, 600);
    }
  };

  const updateStats = (logs) => {
    const total = logs.length;
    if (total === 0) {
      statTotal.textContent = '0';
      statPass.textContent = '0%';
      statRewrite.textContent = '0%';
      statBlock.textContent = '0%';
      return;
    }

    const passes = logs.filter(l => l.action_taken === 'PASS').length;
    const rewrites = logs.filter(l => l.action_taken === 'REWRITE').length;
    const blocks = logs.filter(l => l.action_taken === 'BLOCK').length;
    const sumRisk = logs.reduce((sum, l) => sum + (l.risk_score || 0), 0);

    const passPct = Math.round((passes / total) * 100);
    const rewritePct = Math.round((rewrites / total) * 100);
    const blockPct = Math.round((blocks / total) * 100);
    const avgRisk = Math.round(sumRisk / total);

    statTotal.textContent = total;
    statPass.textContent = `${passPct}%`;
    statRewrite.textContent = `${rewritePct}%`;
    statBlock.textContent = `${blockPct}% (${blocks} logs)`;
  };

  const formatTimestamp = (isoString) => {
    try {
      const date = new Date(isoString);
      if (isNaN(date.getTime())) return isoString;
      
      const pad = (n) => String(n).padStart(2, '0');
      
      const yyyy = date.getFullYear();
      const mm = pad(date.getMonth() + 1);
      const dd = pad(date.getDate());
      const hh = pad(date.getHours());
      const min = pad(date.getMinutes());
      const ss = pad(date.getSeconds());
      
      return `${yyyy}-${mm}-${dd} ${hh}:${min}:${ss}`;
    } catch {
      return isoString;
    }
  };

  const renderTable = (logs) => {
    tableBody.innerHTML = '';
    logsCount.textContent = `${logs.length} visible`;

    if (logs.length === 0) {
      tableBody.innerHTML = `
        <tr>
          <td colspan="8">
            <div class="empty-state">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
              </svg>
              <p>No audit logs available yet. Make a call to /analyze first.</p>
            </div>
          </td>
        </tr>
      `;
      return;
    }

    logs.forEach(log => {
      const tr = document.createElement('tr');
      
      // Action badge
      const actionLower = (log.action_taken || 'pass').toLowerCase();
      const actionBadge = `<span class="badge-action ${actionLower}">${log.action_taken}</span>`;
      
      // Risk level
      let riskClass = 'low';
      if (log.risk_score > 65) riskClass = 'high';
      else if (log.risk_score > 30) riskClass = 'medium';
      
      const riskBadge = `<span class="score-badge ${riskClass}">${log.risk_score}</span>`;

      // Prompt cell
      const promptEscaped = escapeHtml(log.prompt || '');
      const userEscaped = escapeHtml(log.user_id || 'Anonymous');
      const evidenceString = log.detection_evidence || '';

      tr.innerHTML = `
        <td class="cell-timestamp">${formatTimestamp(log.timestamp)}</td>
        <td class="cell-user" title="${userEscaped}">${userEscaped}</td>
        <td class="cell-prompt" data-prompt="${encodeURIComponent(log.prompt)}">${promptEscaped}</td>
        <td class="cell-risk-score">${riskBadge}</td>
        <td><span class="cell-category">${escapeHtml(log.attack_category || 'safe')}</td>
        <td>${actionBadge}</td>
        <td>
          <button class="btn-inspect" data-evidence="${encodeURIComponent(evidenceString)}">Inspect</button>
        </td>
      `;

      // Bind prompt cell click
      const promptCell = tr.querySelector('.cell-prompt');
      promptCell.addEventListener('click', () => {
        const fullPrompt = decodeURIComponent(promptCell.getAttribute('data-prompt'));
        openModal('Inspecting Prompt', fullPrompt);
      });

      // Bind inspect button click
      const inspectBtn = tr.querySelector('.btn-inspect');
      inspectBtn.addEventListener('click', () => {
        const evidence = decodeURIComponent(inspectBtn.getAttribute('data-evidence'));
        openModal('Detection Evidence Details', evidence || 'No detailed evidence found.');
      });

      tableBody.appendChild(tr);
    });
  };

  const escapeHtml = (unsafe) => {
    return unsafe
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  };

  const showError = (msg) => {
    tableBody.innerHTML = `
      <tr>
        <td colspan="8" style="text-align: center; color: var(--color-block); padding: 2rem;">
          Error: ${msg}
        </td>
      </tr>
    `;
  };

  refreshBtn.addEventListener('click', loadDashboardData);

  // Initial load
  loadDashboardData();
});
