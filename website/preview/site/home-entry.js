// The homepage is the single location for registration, sign-in and recovery.
const params = new URLSearchParams(location.search);
let passwordResetToken = '';
if (params.get('view') === 'reset-password') {
  const candidate = new URLSearchParams(location.hash.slice(1)).get('token') || '';
  // Clear the address before loading another module or making an async request.
  history.replaceState(null, '', location.pathname + location.search + '#contributor-access');
  if (/^[A-Za-z0-9_-]{32,256}$/.test(candidate)) passwordResetToken = candidate;
}
const panel = document.querySelector('#contributor-access');
const safeNext = value => {
  if (!value) return null;
  try {
    const target = new URL(value, location.href);
    if (target.origin === location.origin && target.pathname === '/contribute.html'
        && !target.username && !target.password
        && !['login', 'register', 'forgot-password', 'reset-password'].includes(target.searchParams.get('view'))) return target.pathname + target.search + target.hash;
  } catch { /* Ignore malformed or external return locations. */ }
  return null;
};
const next = safeNext(params.get('next'));
for (const [id, mode] of [['contributor-signin', 'login'], ['contributor-register', 'register']]) {
  const entry = document.getElementById(id);
  if (entry && next) {
    const query = new URLSearchParams({view: mode, next});
    entry.href = '/?' + query + '#contributor-access';
  }
}
if (panel && ['login', 'register', 'forgot-password', 'reset-password'].includes(params.get('view'))) {
  panel.hidden = false;
  try {
    const workspace = await import('./workspace.js');
    await workspace.initializeHomeAccount(passwordResetToken);
    passwordResetToken = '';
    // Let the document finish its fragment navigation and form layout before
    // bringing the account section into view; avoid a second, stale anchor jump.
    const revealAccount = () => requestAnimationFrame(() => requestAnimationFrame(() => {
      const header = document.querySelector('.site-header');
      const offset = (header?.getBoundingClientRect().height || 0) + 24;
      const top = panel.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({top: Math.max(0, top), behavior: 'instant'});
      const heading = panel.querySelector('h2');
      if (heading) { heading.tabIndex = -1; heading.focus({preventScroll: true}); }
    }));
    if (document.readyState === 'complete') revealAccount();
    else window.addEventListener('load', revealAccount, {once: true});
  } catch {
    passwordResetToken = '';
    const area = panel.querySelector('#workspace');
    const message = document.createElement('p');
    message.textContent = 'Contributor access could not load. Keep browsing, or return to the main page and try again.';
    const retry = document.createElement('a');
    retry.href = '/'; retry.textContent = 'Back to main page'; retry.className = 'text-link';
    area.replaceChildren(message, retry);
  }
}
