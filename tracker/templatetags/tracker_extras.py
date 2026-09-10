"""Small presentation helpers for the InternTrack templates.

These exist so the templates can render the master design's logo chips and
avatars without the view having to carry display-only data around.
"""

from django import template

register = template.Library()

# The accent palette from the design tokens, minus the two lightest shades,
# which do not carry white text well.
CHIP_COLORS = ['#77B2F1', '#F4512D', '#0B2D66', '#17A34A', '#ED940F', '#600404']


@register.filter
def chip_color(name):
    """A stable accent colour for a company name.

    The same company always gets the same colour, across pages and sessions,
    without storing anything on the model.
    """
    if not name:
        return CHIP_COLORS[0]
    return CHIP_COLORS[sum(ord(c) for c in str(name)) % len(CHIP_COLORS)]


@register.filter
def initials(value, limit=2):
    """First letters of the first two words, e.g. "Alex Rivera" -> "AR"."""
    words = str(value or '').split()
    if not words:
        return '?'
    return ''.join(w[0] for w in words[:limit]).upper()


@register.simple_tag(takes_context=True)
def query_string(context, **kwargs):
    """Current GET parameters with some keys replaced.

    Lets a filter pill or pagination link change one parameter and keep the
    rest: {% query_string status='Applied' page=1 %}
    """
    params = context['request'].GET.copy()
    for key, value in kwargs.items():
        if value in (None, ''):
            params.pop(key, None)
        else:
            params[key] = value
    encoded = params.urlencode()
    return f'?{encoded}' if encoded else '?'
