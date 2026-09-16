from functools import wraps

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect


def session_required(url_name="login"):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get("erp_session"):
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    return JsonResponse(
                        {"error": "Sesión expirada. Por favor inicia sesión nuevamente."},
                        status=401
                    )
                messages.error(
                    request,
                    "La sesión ha expirado. Por favor inicia sesión nuevamente.",
                )
                return redirect(url_name)

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator
