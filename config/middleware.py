# middleware.py
import datetime
import logging

from django.utils import timezone
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

from apps.login.services import get_logout
from apps.login.user import ERPUser

logger = logging.getLogger(__name__)

class SessionTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/static") or request.path in ["/favicon.ico", "/error"]:
            return self.get_response(request)
        if request.session.get("erp_session"):
            ahora = timezone.now()
            last_activity = request.session.get("last_activity")

            if last_activity:
                ultima_dt = None
                # Caso 1: timestamp numérico
                try:
                    ultima_dt = datetime.datetime.fromtimestamp(
                        float(last_activity),
                        tz=timezone.get_current_timezone(),
                    )
                except Exception:
                    # Caso 2: string ISO
                    try:
                        ultima_dt = datetime.datetime.fromisoformat(str(last_activity))
                        if timezone.is_naive(ultima_dt):
                            ultima_dt = timezone.make_aware(
                                ultima_dt, timezone.get_current_timezone()
                            )
                    except Exception:
                        ultima_dt = ahora  # fallback seguro

                tiempo_inactivo = (ahora - ultima_dt).total_seconds()

                if tiempo_inactivo > settings.SESSION_COOKIE_AGE:
                    request.session.flush()
                    return redirect(settings.LOGIN_URL)
                else:
                    logger.info(f"Sesión activa: inactivo {tiempo_inactivo}s")

            # Actualiza siempre en formato timestamp
            request.session["last_activity"] = ahora.timestamp()
            request.session.modified = True 
        return self.get_response(request)
    
class ErrorRedirectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        error_url = reverse("error_page")

        if request.path == error_url:
            return self.get_response(request)

        try:
            response = self.get_response(request)

            if response.status_code == 404:
                logout(request)
                return redirect("error_page")

            return response

        except Exception:
            logout(request)

            return redirect("error_page")
        
class SessionUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 🔑 Ignorar estáticos, favicons y llamadas de DevTools para no romper el flujo
        if request.path in ['/favicon.ico', '/error/'] or request.path.startswith('/.well-known/'):
            return self.get_response(request)

        # Si existe sesión activa, asignamos el ERPUser
        if hasattr(request, "session") and request.session.get("erp_session"):
            erp_sid = request.session.get("erp_sid")
            username = request.session.get("username")
            request.user = ERPUser(erp_sid, username, erp_sid, [])

        return self.get_response(request)