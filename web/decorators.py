
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def solo_admin(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        es_admin = (
            request.user.is_superuser
            or request.user.groups.filter(
                name="Administradores"
            ).exists()
        )

        if es_admin:
            return view_func(request, *args, **kwargs)

        return redirect("panel_personal")

    return wrapper


def solo_personal(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        return redirect("inicio")

    return wrapper