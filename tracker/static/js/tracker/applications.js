/* InternTrack — tracker layer, applications list.
   Filtering, sorting and paging are all GET parameters handled by the view.
   This file only makes the controls nicer to use. */
(function () {
  'use strict';

  var form = IT.$('list-filters');

  /* --- Show / hide the filter toolbar ---------------------------------- */
  var toggle = IT.$('toggle-filter');
  if (toggle && form) {
    /* Keep it open when the user arrived with a filter already applied. */
    var params = new URLSearchParams(window.location.search);
    if (params.get('q') || params.get('sort')) form.hidden = false;

    toggle.addEventListener('click', function () {
      form.hidden = !form.hidden;
      toggle.setAttribute('aria-expanded', String(!form.hidden));
      if (!form.hidden) IT.$('q').focus();
    });
  }

  /* --- Sorting submits immediately ------------------------------------- */
  var sort = IT.$('sort');
  if (sort && form) sort.addEventListener('change', function () { form.submit(); });

  /* --- Whole table row opens the application --------------------------- */
  /* Each <tr> carries data-href. The row also holds a real <a> in the first
     cell, so keyboard users and screen readers get a proper link. */
  document.addEventListener('click', function (e) {
    if (e.target.closest('a, button, input, label')) return;
    var row = e.target.closest('tr[data-href]');
    if (row) window.location.href = row.dataset.href;
  });
})();
