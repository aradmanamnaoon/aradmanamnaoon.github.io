(function () {
  'use strict';

  const navigation = document.querySelector('nav[aria-label="Primary navigation"]');
  const links = navigation?.querySelector('.site-nav-links, .nav-links');
  if (navigation && links) {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'nav-toggle';
    button.setAttribute('aria-expanded', 'false');
    button.setAttribute('aria-controls', 'primary-nav-links');
    button.setAttribute('aria-label', 'Open navigation');
    button.innerHTML = '<span class="nav-toggle-icon" aria-hidden="true">☰</span><span>Menu</span>';
    links.id = 'primary-nav-links';
    navigation.insertBefore(button, links);
    navigation.classList.add('mobile-nav-ready');

    function closeMenu(returnFocus) {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Open navigation');
      links.removeAttribute('data-open');
      if (returnFocus) button.focus();
    }

    button.addEventListener('click', function () {
      const open = button.getAttribute('aria-expanded') !== 'true';
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      if (open) links.setAttribute('data-open', 'true');
      else links.removeAttribute('data-open');
    });
    links.addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu(false);
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape' && button.getAttribute('aria-expanded') === 'true') {
        closeMenu(true);
      }
    });
    document.addEventListener('click', function (event) {
      if (!navigation.contains(event.target)) closeMenu(false);
    });
    const desktop = window.matchMedia('(min-width: 768px)');
    desktop.addEventListener?.('change', function (event) {
      if (event.matches) closeMenu(false);
    });
  }

  const retry = document.querySelector('[data-retry]');
  retry?.addEventListener('click', function () { window.location.reload(); });

  const form = document.querySelector('form.contact-form');
  if (form && window.fetch) {
    const submit = form.querySelector('[type="submit"]');
    const status = document.createElement('p');
    status.className = 'contact-form-status';
    status.setAttribute('role', 'status');
    status.setAttribute('aria-live', 'polite');
    submit?.insertAdjacentElement('afterend', status);
    form.addEventListener('submit', async function (event) {
      if (!form.checkValidity()) return;
      event.preventDefault();
      if (form.getAttribute('aria-busy') === 'true') return;
      form.setAttribute('aria-busy', 'true');
      if (submit) submit.disabled = true;
      status.dataset.state = 'loading';
      status.textContent = 'Sending your message…';
      try {
        const response = await fetch(form.action, {
          method: 'POST', body: new FormData(form),
          headers: { Accept: 'application/json' }
        });
        if (!response.ok) throw new Error('Form submission failed');
        form.reset();
        status.dataset.state = 'success';
        status.textContent = 'Message sent. Thank you — I will reply by email.';
      } catch (_) {
        status.dataset.state = 'error';
        status.textContent = 'The message did not go through. Please try again or use the LinkedIn link above.';
      } finally {
        form.removeAttribute('aria-busy');
        if (submit) submit.disabled = false;
      }
    });
  }

  if ('serviceWorker' in navigator &&
      (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', function () {
      navigator.serviceWorker.register('/service-worker.js').catch(function () {
        // The portfolio remains usable when offline support is unavailable.
      });
    });
  }
})();
