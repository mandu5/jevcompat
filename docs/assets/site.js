/* Read-only interface to committed conformance reports. No requests to model servers. */
(() => {
  'use strict';
  const source = 'https://github.com/mandu5/jevcompat/blob/main/';
  const byId = id => document.getElementById(id);
  const dialog = byId('inspection');
  let data, requirements, active = { server: 0, requirement: 0 };
  const text = (tag, content, className) => {
    const node = document.createElement(tag);
    node.textContent = content;
    if (className) node.className = className;
    return node;
  };
  const link = (label, href) => {
    const node = text('a', label); node.href = href; return node;
  };
  document.querySelector('.theme-toggle').addEventListener('click', event => {
    const light = document.documentElement.dataset.theme !== 'light';
    document.documentElement.dataset.theme = light ? 'light' : 'dark';
    event.currentTarget.textContent = light ? 'Dark' : 'Light';
    event.currentTarget.setAttribute('aria-label', `Switch to ${light ? 'dark' : 'light'} theme`);
  });

  function showExchange(report, index) {
    const exchange = report.exchanges[index];
    byId('exchange').hidden = !exchange;
    if (!exchange) return;
    byId('exchange-title').textContent = `${exchange.case} · ${exchange.method} ${exchange.path} · HTTP ${exchange.status}`;
    byId('request-body').textContent = JSON.stringify(exchange.request, null, 2);
    // Preserve recorded response text: parsing and reserializing can hide byte-level differences.
    byId('response-body').textContent = exchange.response;
  }

  function inspect(server, requirement, open = true) {
    active = { server, requirement };
    const run = data.reports[server];
    const result = run.report.results.find(item => item.id === requirements[requirement].id);
    document.querySelectorAll('[data-cell]').forEach(cell => {
      const selected = cell.dataset.cell === `${server},${requirement}`;
      cell.setAttribute('aria-selected', String(selected));
      cell.tabIndex = selected ? 0 : -1;
    });
    byId('matrix-readout').textContent = `${run.server} · ${result.id} · ${result.status} · ${result.title}`;
    byId('inspection-meta').textContent = `${run.server} · ${result.level} · §${result.section} · ${requirement + 1} of ${requirements.length}`;
    byId('inspection-title').textContent = result.title;
    byId('inspection-status').textContent = `${result.id} — ${result.status === 'skip' ? 'Not tested' : result.status}`;
    byId('server-picker').querySelectorAll('button').forEach((button, index) => button.setAttribute('aria-pressed', String(index === server)));
    byId('spec-excerpt').textContent = data.requirements[result.id] || result.title;
    byId('spec-link').href = `${source}SPEC.md#${result.id}`;
    byId('report-link').href = `${source}results/${run.server}/report.md`;
    byId('run-link').href = `${source}results/${run.server}/RUN.md`;
    byId('finding-list').replaceChildren();
    byId('finding-summary').textContent = result.reason || (result.findings.length
      ? `${result.findings.length} recorded finding${result.findings.length === 1 ? '' : 's'}. Select one to inspect its exchange.`
      : `No failures recorded for this requirement. ${result.cases.length} associated case${result.cases.length === 1 ? '' : 's'}.`);
    result.findings.forEach((finding, index) => {
      const button = text('button', `${finding.case}: ${finding.message}`);
      button.type = 'button';
      button.setAttribute('aria-pressed', String(index === 0));
      button.addEventListener('click', () => {
        byId('finding-list').querySelectorAll('button').forEach(node => node.setAttribute('aria-pressed', String(node === button)));
        showExchange(run.report, finding.exchange);
      });
      byId('finding-list').append(button);
    });
    const firstExchange = result.findings[0]?.exchange ?? run.report.exchanges.findIndex(item => result.cases.includes(item.case));
    showExchange(run.report, firstExchange);
    if (open && !dialog.open) dialog.showModal();
  }

  function render() {
    requirements = data.reports[0].report.results;
    byId('server-headers').replaceChildren();
    byId('matrix').replaceChildren();
    byId('run-list').replaceChildren();
    byId('server-picker').replaceChildren();
    data.reports.forEach(({ server, report }, index) => {
      const chooseServer = text('button', server);
      chooseServer.type = 'button';
      chooseServer.addEventListener('click', () => inspect(index, active.requirement));
      byId('server-picker').append(chooseServer);
      const heading = document.createElement('div');
      heading.append(text('b', server), text('small', `${report.summary.MUST.passed}/${report.summary.MUST.tested} MUST`));
      byId('server-headers').append(heading);
      const row = text('article', '', 'run-row');
      const title = document.createElement('div');
      title.append(text('h3', server), text('p', `Spec ${report.spec_version} · ${report.seconds}s recorded run`));
      row.append(title, text('span', `${report.summary.MUST.passed}/${report.summary.MUST.tested} MUST`), text('span', `${report.summary.SHOULD.passed}/${report.summary.SHOULD.tested} SHOULD`), text('span', report.summary.verdict, report.summary.conformant ? 'conformant' : ''), link('Read report ↗', `${source}results/${server}/report.md`));
      byId('run-list').append(row);
    });
    requirements.forEach((requirement, rowIndex) => {
      const row = text('div', '', 'weave-row');
      row.setAttribute('role', 'row'); row.setAttribute('aria-rowindex', rowIndex + 1);
      const number = text('span', String(rowIndex + 1).padStart(2, '0')); number.setAttribute('aria-hidden', 'true'); row.append(number);
      data.reports.forEach(({ server, report }, columnIndex) => {
        const result = report.results.find(item => item.id === requirement.id);
        const cell = text('button', '', result.status);
        cell.type = 'button'; cell.dataset.cell = `${columnIndex},${rowIndex}`;
        cell.setAttribute('role', 'gridcell'); cell.setAttribute('aria-colindex', columnIndex + 1);
        cell.setAttribute('aria-label', `${server}: ${result.id}; ${result.level}; ${result.status}. ${result.title}`);
        cell.setAttribute('aria-selected', 'false'); cell.tabIndex = rowIndex === 0 && columnIndex === 0 ? 0 : -1;
        cell.addEventListener('click', () => inspect(columnIndex, rowIndex));
        cell.addEventListener('keydown', event => {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            inspect(columnIndex, rowIndex);
            return;
          }
          const offsets = { ArrowLeft: [-1, 0], ArrowRight: [1, 0], ArrowUp: [0, -1], ArrowDown: [0, 1] };
          if (!offsets[event.key]) return;
          event.preventDefault();
          const [dx, dy] = offsets[event.key];
          const nextColumn = Math.max(0, Math.min(data.reports.length - 1, columnIndex + dx));
          const nextRow = Math.max(0, Math.min(requirements.length - 1, rowIndex + dy));
          inspect(nextColumn, nextRow, false);
          document.querySelector(`[data-cell="${nextColumn},${nextRow}"]`).focus();
        });
        row.append(cell);
      });
      byId('matrix').append(row);
    });
    document.documentElement.dataset.evidence = 'ready';
  }

  async function load() {
    byId('data-error').hidden = true;
    try {
      const response = await fetch('assets/recorded-runs.json');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      data = await response.json();
      if (data.reports.length !== 8 || data.reports.some(run => run.report.results.length !== 48)) throw new Error('Incomplete recorded reports');
      render();
    } catch {
      byId('data-error').hidden = false;
      document.documentElement.dataset.evidence = 'error';
    }
  }
  byId('retry').addEventListener('click', load);
  byId('browse-requirements').addEventListener('click', () => { if (data) inspect(active.server, active.requirement); });
  byId('close-inspection').addEventListener('click', () => dialog.close());
  byId('previous-requirement').addEventListener('click', () => inspect(active.server, (active.requirement + requirements.length - 1) % requirements.length));
  byId('next-requirement').addEventListener('click', () => inspect(active.server, (active.requirement + 1) % requirements.length));
  load();
})();
