def user_display(request):
    """Makes {{ initials }}, {{ display_name }}, and {{ profile }} available
    on every page, since base.html's top bar uses them and every page extends base.html."""
    if request.user.is_authenticated:
        full_name = request.user.get_full_name() or request.user.username
        words = full_name.split()
        initials = ''.join(w[0] for w in words[:2]).upper() if words else '?'
        return {
            'initials': initials,
            'display_name': full_name,
            'profile': getattr(request.user, 'profile', None),
        }
    return {}