/* ─── BandaFlow Shared Utilities ─────────────────────────────────────────── */

// CSRF token for Django
function getCookie(name) {
  let v = null;
  if (document.cookie && document.cookie !== '') {
    document.cookie.split(';').forEach(c => {
      const t = c.trim();
      if (t.startsWith(name + '=')) v = decodeURIComponent(t.slice(name.length + 1));
    });
  }
  return v;
}
const CSRF = getCookie('csrftoken');

async function apiFetch(url, options = {}) {
  const defaults = {
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF },
    credentials: 'same-origin',
  };
  const res = await fetch(url, { ...defaults, ...options, headers: { ...defaults.headers, ...(options.headers || {}) } });
  return res.json();
}

// Toast notifications
function showToast(msg, type = 'success') {
  const container = document.getElementById('toast-container') || (() => {
    const el = document.createElement('div');
    el.id = 'toast-container';
    el.className = 'toast-container';
    document.body.appendChild(el);
    return el;
  })();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = msg;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3800);
}

// Format currency
function ksh(amount) {
  const n = parseFloat(amount) || 0;
  return 'Ksh ' + n.toLocaleString('en-KE', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// Modal helpers
function openModal(id) {
  document.getElementById(id).classList.add('open');
}
function closeModal(id) {
  document.getElementById(id).classList.remove('open');
}

// Close modal on overlay click
document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('open');
  }
});

// Password eye toggles
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.eye-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.closest('.input-wrap').querySelector('input');
      if (!input) return;
      const isPass = input.type === 'password';
      input.type = isPass ? 'text' : 'password';
      btn.innerHTML = isPass ? eyeOffIcon() : eyeIcon();
    });
  });
});

function eyeIcon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>`;
}

function eyeOffIcon() {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>`;
}

// Ticker / cycling animation
function startTicker(items, containerId, renderFn) {
  const container = document.getElementById(containerId);
  if (!container || !items.length) return;
  container.innerHTML = '';

  items.forEach((item, i) => {
    const el = document.createElement('div');
    el.className = 'ticker-item' + (i === 0 ? ' visible' : '');
    el.innerHTML = renderFn(item);
    container.appendChild(el);
  });

  if (items.length <= 1) return;

  let current = 0;
  setInterval(() => {
    const els = container.querySelectorAll('.ticker-item');
    els[current].classList.remove('visible');
    current = (current + 1) % els.length;
    els[current].classList.add('visible');
  }, 5000);
}

// Active nav link
function setActiveNav(page) {
  document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.page === page);
  });
}
