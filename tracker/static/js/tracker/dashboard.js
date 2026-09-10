/* InternTrack — tracker layer, dashboard.
   Draws the donut and the journey bars from the counts the view puts in
   #dashboard-stats via {{ stats|json_script:"dashboard-stats" }}.
   No data is computed here — the server owns the numbers. */
(function () {
  'use strict';

  var stats = IT.readJSON('dashboard-stats', null);
  if (!stats) return;

  /* Keys match Internship.STATUS_CHOICES, lowercased. */
  var STATUS = {
    applied:   { label: 'Applied',   color: '#77B2F1' },
    interview: { label: 'Interview', color: '#F4512D' },
    accepted:  { label: 'Accepted',  color: '#17A34A' },
    rejected:  { label: 'Rejected',  color: '#600404' },
    waiting:   { label: 'Waiting',   color: '#FAD02B' }
  };
  var ORDER = ['waiting', 'applied', 'interview', 'accepted', 'rejected'];

  /* --- Journey bars ---------------------------------------------------- */
  var journey = IT.$('journey');
  if (journey) {
    var stages = ['waiting', 'applied', 'interview', 'accepted'];
    var max = Math.max.apply(null, stages.map(function (k) { return stats[k] || 0; })) || 1;

    journey.innerHTML = stages.map(function (k) {
      var n = stats[k] || 0;
      var pct = Math.round((n / max) * 100);
      return '<div class="journey-row"><span>' + STATUS[k].label + '</span>' +
        '<div class="track"><i style="width:' + pct + '%;background:' + STATUS[k].color + '"></i></div>' +
        '<b>' + n + '</b></div>';
    }).join('');
  }

  /* --- Donut ----------------------------------------------------------- */
  var donut = IT.$('donut');
  if (!donut) return;

  var parts = ORDER.map(function (k) {
    return { key: k, n: stats[k] || 0, color: STATUS[k].color };
  }).filter(function (p) { return p.n > 0; });

  var total = parts.reduce(function (sum, p) { return sum + p.n; }, 0) || 1;
  var R = 62;
  var CIRC = 2 * Math.PI * R;
  var offset = 0;

  var rings = parts.map(function (p) {
    var len = (p.n / total) * CIRC;
    var seg = '<circle cx="80" cy="80" r="' + R + '" fill="none" stroke="' + p.color +
      '" stroke-width="22" stroke-dasharray="' + (len - 3) + ' ' + (CIRC - len + 3) +
      '" stroke-dashoffset="' + (-offset) + '" transform="rotate(-90 80 80)" stroke-linecap="butt"></circle>';
    offset += len;
    return seg;
  }).join('');

  donut.innerHTML =
    '<svg viewBox="0 0 160 160" width="180" height="180" role="img" aria-label="Applications by status">' +
    '<circle cx="80" cy="80" r="' + R + '" fill="none" stroke="#EEF1F7" stroke-width="22"></circle>' + rings +
    '<text x="80" y="76" text-anchor="middle" font-size="26" font-weight="700" fill="#0B2D66">' +
    (stats.total || 0) + '</text>' +
    '<text x="80" y="96" text-anchor="middle" font-size="11" fill="#7C8AA0">Total</text></svg>';

  var legend = IT.$('legend');
  if (legend) {
    legend.innerHTML = ORDER.map(function (k) {
      return '<div><i style="background:' + STATUS[k].color + '"></i>' +
        STATUS[k].label + '<b>' + (stats[k] || 0) + '</b></div>';
    }).join('');
  }
})();
