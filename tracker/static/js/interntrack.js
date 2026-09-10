/* InternTrack — progressive enhancement.
   Every feature here has a working no-JS fallback: rows are real links,
   filters submit as a normal GET form, and the export buttons fall back to
   plain navigation. Nothing on this page depends on the script loading. */
(function () {
  'use strict';

  /* ------------------------------------------------------------------ toast */
  function toast(message) {
    var existing = document.querySelector('.toast');
    if (existing) existing.remove();

    var node = document.createElement('div');
    node.className = 'toast';
    node.setAttribute('role', 'status');
    node.textContent = message;
    document.body.appendChild(node);
    setTimeout(function () { node.remove(); }, 2600);
  }

  /* --------------------------------------------------- collapsible filters */
  function initToggles() {
    document.addEventListener('click', function (event) {
      var trigger = event.target.closest('[data-toggle]');
      if (!trigger) return;

      var target = document.getElementById(trigger.dataset.toggle);
      if (!target) return;

      var willShow = target.hasAttribute('hidden');
      target.toggleAttribute('hidden', !willShow);
      trigger.setAttribute('aria-expanded', String(willShow));

      if (willShow) {
        var firstInput = target.querySelector('input, select');
        if (firstInput) firstInput.focus();
      }
    });
  }

  /* ------------------------------------------------------- clickable rows */
  function initRowLinks() {
    document.addEventListener('click', function (event) {
      var row = event.target.closest('tr.row-link');
      if (!row || !row.dataset.href) return;
      // Let real links, buttons and text selection behave normally.
      if (event.target.closest('a, button, input, label')) return;
      if (window.getSelection && String(window.getSelection())) return;
      window.location.href = row.dataset.href;
    });
  }

  /* -------------------------------------------------- surface form errors */
  function initFieldErrors() {
    Array.prototype.forEach.call(document.querySelectorAll('.field'), function (field) {
      if (!field.querySelector('ul.errorlist')) return;
      var control = field.querySelector('input, select, textarea');
      if (control) control.classList.add('has-error');
    });

    var firstError = document.querySelector('.field .has-error');
    if (firstError) firstError.focus({ preventScroll: false });
  }

  /* ---------------------------------------------- status-driven interview */
  function initInterviewSection() {
    var status = document.getElementById('id_status');
    var section = document.getElementById('interview-section');
    if (!status || !section) return;

    // Keep it open if the server sent back errors inside it.
    var hasErrors = !!section.querySelector('ul.errorlist');

    function sync() {
      var show = status.value === 'interview' || hasErrors;
      section.toggleAttribute('hidden', !show);
    }

    status.addEventListener('change', sync);
    sync();
  }

  /* ----------------------------------------------------------- export page */
  function initExport() {
    var urls = window.INTERNTRACK_EXPORT;
    if (!urls) return;

    var statusEl = document.getElementById('export-status');
    var statusSelect = document.getElementById('e-status');
    var filenameInput = document.getElementById('e-filename');

    function say(message) {
      if (statusEl) statusEl.textContent = message;
    }

    function buildUrl(kind) {
      var params = new URLSearchParams();
      var name = (filenameInput && filenameInput.value.trim()) || '';
      if (name) params.set('filename', name);
      if (statusSelect && statusSelect.value) params.set('status', statusSelect.value);
      var query = params.toString();
      return urls[kind] + (query ? '?' + query : '');
    }

    document.addEventListener('click', function (event) {
      var button = event.target.closest('[data-export]');
      if (!button) return;

      var kind = button.dataset.export;
      if (!urls[kind]) return;

      event.preventDefault();
      say('Preparing your ' + kind.toUpperCase() + '…');

      fetch(buildUrl(kind), { credentials: 'same-origin' })
        .then(function (response) {
          if (!response.ok) throw new Error('The server could not generate that file.');
          return response.blob();
        })
        .then(function (blob) {
          var name = ((filenameInput && filenameInput.value.trim()) ||
                      'interntrack_export').replace(/[^A-Za-z0-9_-]/g, '_');
          var link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = name + '.' + kind;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          setTimeout(function () { URL.revokeObjectURL(link.href); }, 1000);
          say('Downloaded ' + name + '.' + kind + '.');
          toast('Export ready');
        })
        .catch(function (error) {
          say('Something went wrong: ' + error.message);
        });
    });
  }

  /* -------------------------------------------------------- message toasts */
  function initMessages() {
    var alerts = document.querySelectorAll('.alerts .alert');
    if (alerts.length !== 1) return;
    // A single message reads better as a transient toast than a banner.
    var alert = alerts[0];
    if (alert.classList.contains('alert-error')) return;
    toast(alert.textContent.trim());
    alert.parentElement.remove();
  }

  function ready(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  ready(function () {
    initToggles();
    initRowLinks();
    initFieldErrors();
    initInterviewSection();
    initExport();
    initMessages();
  });

  window.InternTrack = { toast: toast };
})();
