'use strict';

const sidebarToggle = document.getElementById('sidebarToggle');
const sidebar = document.getElementById('sidebar');
const layout = document.getElementById('layout');

if (sidebarToggle && sidebar) {
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (window.innerWidth <= 768) {
      if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    }
  });
}

const toastEl = document.getElementById('toast');
const toastMessage = document.getElementById('toastMessage');
const toastIcon = document.getElementById('toastIcon');
let toastTimeout = null;

function showToast(message, type = 'info', duration = 3500) {
  if (!toastEl) return;

  if (toastTimeout) clearTimeout(toastTimeout);

  if (toastMessage) toastMessage.textContent = message;

  const icons = {
    success: 'check_circle',
    error: 'error',
    info: 'info',
    warning: 'warning',
  };

  if (toastIcon) toastIcon.textContent = icons[type] || 'info';

  toastEl.classList.remove('toast--success', 'toast--error', 'toast--info', 'toast--warning');
  toastEl.classList.add(`toast--${type}`);

  toastEl.classList.add('show');

  toastTimeout = setTimeout(() => {
    toastEl.classList.remove('show');
  }, duration);
}

window.showToast = showToast;

async function loadSidebarStats() {
  try {
    const res = await fetch('/api/stats/');
    if (!res.ok) return;
    const data = await res.json();

    const onlineEl = document.getElementById('sb-online');
    const offlineEl = document.getElementById('sb-offline');
    const slowEl = document.getElementById('sb-slow');

    if (onlineEl) onlineEl.textContent = data.online_count;
    if (offlineEl) offlineEl.textContent = data.offline_count;
    if (slowEl) slowEl.textContent = data.slow_count;
  } catch (e) {

  }
}

document.addEventListener('DOMContentLoaded', () => {

  const mainContent = document.querySelector('.main-content');
  if (mainContent) {
    mainContent.style.opacity = '0';
    mainContent.style.transform = 'translateY(8px)';
    mainContent.style.transition = 'opacity 300ms ease, transform 300ms ease';

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        mainContent.style.opacity = '1';
        mainContent.style.transform = 'translateY(0)';
      });
    });
  }

  loadSidebarStats();

  setInterval(loadSidebarStats, 30000);
});

document.addEventListener('keydown', (e) => {

  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    const searchInput = document.getElementById('monitorSearch');
    if (searchInput) {
      searchInput.focus();
      searchInput.select();
    }
  }

  if (e.key === 'Escape' && window.innerWidth <= 768) {
    if (sidebar) sidebar.classList.remove('open');
  }
});

document.querySelectorAll('.alert-banner').forEach(banner => {
  setTimeout(() => {
    banner.style.transition = 'opacity 500ms ease, transform 500ms ease';
    banner.style.opacity = '0';
    banner.style.transform = 'translateY(-8px)';
    setTimeout(() => banner.remove(), 500);
  }, 5000);
});

document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', (e) => {
    if (!confirm(el.dataset.confirm)) {
      e.preventDefault();
    }
  });
});

function formatRelativeTime(dateStr) {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  if (diffSec < 60) return 'just now';
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHour < 24) return `${diffHour}h ago`;
  return `${diffDay}d ago`;
}

window.formatRelativeTime = formatRelativeTime;

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}

window.debounce = debounce;

const liveIndicator = document.getElementById('liveIndicator');
if (liveIndicator) {

  window.flashLive = () => {
    liveIndicator.style.opacity = '0.5';
    setTimeout(() => { liveIndicator.style.opacity = '1'; }, 300);
  };
}
