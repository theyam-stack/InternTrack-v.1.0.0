/* InternTrack — tracker layer, add/edit application form.
   Moved out of the inline <script> that used to sit in internship_form.html.
   Shows the interview block only when the status is "Interview", which is
   the one status the view reads interview_date / interview_type for. */
(function () {
  'use strict';

  var status = IT.$('id_status');
  var section = IT.$('interview-section');
  if (!status || !section) return;

  function sync() {
    var wanted = status.value === 'Interview';
    section.hidden = !wanted;
    /* Don't post a half-filled interview for a non-interview application. */
    IT.$('id_interview_date').disabled = !wanted;
    IT.$('id_interview_type').disabled = !wanted;
  }

  status.addEventListener('change', sync);
  sync(); /* also on load, for editing an existing Interview-status record */
})();
