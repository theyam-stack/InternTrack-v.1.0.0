/* InternTrack — base layer.
   Helpers shared by the registration and tracker scripts.
   Loaded on every page, before any section script. */
(function (w) {
  'use strict';

  function $(id) { return document.getElementById(id); }

  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function initials(name) {
    return String(name || '?').trim().split(/\s+/).slice(0, 2)
      .map(function (word) { return word.charAt(0); }).join('').toUpperCase();
  }

  /* Transient confirmation message. Replaces any toast already on screen. */
  function toast(msg) {
    var old = document.querySelector('.toast');
    if (old) old.remove();
    var node = document.createElement('div');
    node.className = 'toast';
    node.setAttribute('role', 'status');
    node.textContent = msg;
    document.body.appendChild(node);
    setTimeout(function () { node.remove(); }, 2600);
  }

  /* Reads a {{ value|json_script:"id" }} block. Returns fallback if absent. */
  function readJSON(id, fallback) {
    var node = $(id);
    if (!node) return fallback;
    try { return JSON.parse(node.textContent); } catch (err) { return fallback; }
  }

  w.IT = { $: $, esc: esc, initials: initials, toast: toast, readJSON: readJSON };
})(window);
