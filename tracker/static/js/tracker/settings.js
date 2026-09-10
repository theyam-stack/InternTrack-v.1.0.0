/* InternTrack — tracker layer, settings.
   Keeps the avatar initials in step with the name field while it is typed.
   Saving is a normal Django form POST. */
(function () {
  'use strict';

  var name = IT.$('id_display_name');
  var avatar = IT.$('set-initials');
  if (!name || !avatar) return;

  name.addEventListener('input', function () {
    avatar.textContent = IT.initials(name.value) || '?';
  });
})();
