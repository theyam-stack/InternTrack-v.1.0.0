/* InternTrack — registration layer.
   Progressive enhancement for the login / register / password-reset pages.
   Every form here posts to Django normally; nothing below is required for
   the page to work with JavaScript disabled. */
(function () {
  'use strict';

  /* --- Password reveal ------------------------------------------------- */
  /* Any [data-reveal="<input id>"] button toggles that field's visibility. */
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-reveal]');
    if (!btn) return;
    e.preventDefault();
    var field = document.getElementById(btn.dataset.reveal);
    if (!field) return;
    var shown = field.type === 'text';
    field.type = shown ? 'password' : 'text';
    btn.textContent = shown ? 'Show' : 'Hide';
    btn.setAttribute('aria-label', shown ? 'Show password' : 'Hide password');
  });

  /* --- Confirm-password match ------------------------------------------ */
  /* Django validates this server-side too; this is only faster feedback. */
  var pass = document.getElementById('id_password1');
  var confirm = document.getElementById('id_password2');

  if (pass && confirm) {
    var note = document.createElement('div');
    note.className = 'hint';
    confirm.parentNode.appendChild(note);

    var check = function () {
      if (!confirm.value) {
        note.textContent = '';
        confirm.setCustomValidity('');
        return;
      }
      var same = pass.value === confirm.value;
      note.textContent = same ? 'Passwords match.' : 'Passwords do not match yet.';
      note.style.color = same ? 'var(--green)' : 'var(--red-deep)';
      confirm.setCustomValidity(same ? '' : 'Passwords do not match.');
    };

    pass.addEventListener('input', check);
    confirm.addEventListener('input', check);
  }
})();
