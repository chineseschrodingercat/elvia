/* One-use Cloudflare Turnstile checks for public credential and mail requests. */
(() => {
  const actions = {'/auth/login':'login','/auth/email-code':'email','/auth/password-reset/request':'reset'};
  let library;
  async function ready() {
    if (window.turnstile) return;
    if (!library) library = new Promise((resolve,reject) => {
      const script = document.createElement('script');
      script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
      script.async = true;
      script.onload = resolve;
      script.onerror = () => { library = null; reject(new Error('The security check could not load. Please try again.')); };
      document.head.append(script);
    });
    await library;
  }
  window.ELVIA_SECURITY = {async token(path) {
    if (!actions[path]) return null;
    const response = await fetch('/api/public-config', {credentials:'same-origin',cache:'no-store'});
    if (!response.ok) throw new Error('The security check is unavailable. Please try again later.');
    const config = await response.json();
    await ready();
    return new Promise((resolve,reject) => {
      const dialog = document.createElement('dialog');
      const heading = document.createElement('h2');
      heading.textContent = 'Security check';
      const hint = document.createElement('p');
      hint.textContent = 'Complete this check to continue.';
      const container = document.createElement('div');
      const cancel = document.createElement('button');
      cancel.type = 'button'; cancel.textContent = 'Cancel'; cancel.className = 'button button-secondary';
      dialog.setAttribute('aria-label','Security check');
      dialog.append(heading,hint,container,cancel); document.body.append(dialog);
      let widget, finished = false;
      const finish = (token,error) => {
        if (finished) return;
        finished = true; clearTimeout(timer);
        if (widget !== undefined) window.turnstile.remove(widget);
        dialog.remove();
        if (error) reject(new Error(error)); else resolve(token);
      };
      const timer = setTimeout(() => finish(null,'The security check expired. Please try again.'),120000);
      cancel.onclick = () => finish(null,'Security check cancelled.');
      dialog.oncancel = event => {event.preventDefault();finish(null,'Security check cancelled.');};
      dialog.showModal();
      try {
        widget = window.turnstile.render(container, {
          sitekey:config.turnstile_sitekey,action:actions[path],
          callback:token => finish(token),
          'error-callback':() => finish(null,'The security check failed. Please try again.'),
          'expired-callback':() => finish(null,'The security check expired. Please try again.'),
        });
      } catch {finish(null,'The security check could not start. Please try again.');}
    });
  }};
})();
