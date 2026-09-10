# InternTrack — frontend built to the UX/UI Master Design

Everything from the master design mockups, rebuilt as a working prototype. No build
step, no framework, no dependencies beyond the Poppins webfont.

## Files

```
demo.html                        all screens, one document
static/css/interntrack.css       design tokens + full component system
static/js/demo-data.js           12 seeded applications (edit freely)
static/js/demo.js                routing, charts, filters, export
```

Open `demo.html` in a browser. `InternTrack.html` is the same thing with the CSS and
JS inlined, for sending to someone as a single file.

## Screens

Login, register, forgot password, dashboard, applications list, add/edit application,
application detail, interviews, companies, search & filter, export, settings.

## Design tokens

Taken straight from the master design. All defined as CSS custom properties at the top
of `interntrack.css`, so a rebrand is a one-block edit.

| Token | Hex | Role |
|---|---|---|
| `--white` | `#FFFFFF` | dominant base |
| `--blue` | `#0B2D66` | navigation, headings, structure |
| `--orange` | `#F4512D` | primary CTA, active nav, key highlights |
| `--yellow` | `#FAD02B` | secondary highlight, tagline, saved state |
| `--amber` | `#ED940F` | secondary accent |
| `--sky` | `#77B2F1` | supportive accent, applied state |
| `--red-deep` | `#600404` | high emphasis, rejected state |
| `--green` | `#17A34A` | accepted state, positive trends |

Type is Poppins throughout: H1 40px bold, H2 28px semibold, H3 20px semibold,
body 14px regular, caption 12px medium.

## What works in the prototype

Status filter pills, keyword search, sort, pagination (5 per page), add/edit/delete,
the donut and journey charts recalculating from live data, interview range filters,
real CSV download, and print-to-PDF. Profile edits update the top bar.

Data lives in memory. Reloading restores the seeded list.

## Backend notes

`TODAY` at the top of `demo.js` is pinned to August 2024 so the seeded interviews read
as upcoming. Change it to `new Date()` when real data arrives.

To wire this into Django:

1. Copy `static/` into your app's static directory and add `{% load static %}` plus
   `{% static 'css/interntrack.css' %}` style references.
2. Split `demo.html` at the `<section id="view-*">` boundaries into templates
   extending a shared `base.html` that holds the sidebar and top bar.
3. Replace the `data-view` links with `{% url %}` tags, and the JS render functions
   with template loops over your context variables.
4. The status vocabulary the templates expect is `saved`, `applied`, `interview`,
   `accepted`, `rejected` — matching the `badge-*` CSS classes.
5. CSV export is currently client-side; move it to a view returning
   `text/csv` when the data is server-side.

## Accessibility and responsiveness

Keyboard focus is visible on every control, `prefers-reduced-motion` is respected,
the layout collapses to a single column with a horizontal nav rail under 860px, and
there is a print stylesheet that strips the chrome for the PDF export.
