"use strict";

// Presentation only. Every write remains independently authorized by the server.
(() => {
  const notices = document.querySelectorAll('[data-visitor-notice]');
  const guestActions = document.querySelector('#contributor-guest-actions');
  const memberActions = document.querySelector('#contributor-member-actions');
  const workspace = document.querySelector('#contributor-workspace');
  fetch('/api/session', {credentials: 'same-origin', cache: 'no-store'})
    .then(response => {
      if (!response.ok) throw new Error('Session unavailable');
      return response.json();
    })
    .then(session => {
      const signedIn = !!session?.user;
      notices.forEach(notice => { notice.hidden = signedIn; });
      if (guestActions) guestActions.hidden = signedIn;
      if (memberActions) memberActions.hidden = !signedIn;
      if (signedIn && workspace) {
        workspace.href = ['admin', 'maintainer'].includes(session.user.role)
          ? '/contribute.html?view=maintainer' : '/contribute.html?view=my-work';
      }
    })
    .catch(() => {
      // Keep browsing available and retain the conservative guest invitation.
    });
})();
