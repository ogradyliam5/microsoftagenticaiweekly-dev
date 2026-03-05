(function () {
  var KEY = 'maiw-theme';
  var root = document.documentElement;

  function safeGetStoredTheme() {
    try {
      var stored = localStorage.getItem(KEY);
      return stored === 'light' || stored === 'dark' ? stored : null;
    } catch (e) {
      return null;
    }
  }

  function preferredTheme() {
    var stored = safeGetStoredTheme();
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    var resolved = theme === 'light' ? 'light' : 'dark';
    root.setAttribute('data-theme', resolved);
    root.classList.remove('theme-dark', 'theme-light');
    root.classList.add(resolved === 'dark' ? 'theme-dark' : 'theme-light');
    root.style.colorScheme = resolved;

    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
      var next = resolved === 'dark' ? 'light' : 'dark';
      btn.setAttribute('aria-label', 'Switch to ' + next + ' mode');
      btn.textContent = resolved === 'dark' ? '☀️ Light' : '🌙 Dark';
    });
  }

  function persistTheme(theme) {
    try {
      localStorage.setItem(KEY, theme);
    } catch (e) {}
  }

  function init() {
    applyTheme(preferredTheme());

    if (window.matchMedia) {
      var media = window.matchMedia('(prefers-color-scheme: dark)');
      var onPrefChange = function (event) {
        if (safeGetStoredTheme()) return;
        applyTheme(event.matches ? 'dark' : 'light');
      };
      if (typeof media.addEventListener === 'function') {
        media.addEventListener('change', onPrefChange);
      } else if (typeof media.addListener === 'function') {
        media.addListener(onPrefChange);
      }
    }

    document.addEventListener('click', function (event) {
      var target = event.target.closest('[data-theme-toggle]');
      if (!target) return;
      var current = root.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      var next = current === 'dark' ? 'light' : 'dark';
      persistTheme(next);
      applyTheme(next);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
