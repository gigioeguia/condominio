import hashlib
import json
import logging
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import login

from django.conf import settings

from .services import login_user, get_logout, get_logged_user
from .forms import LoginForm
from .user import ERPUser
from config.decorators import session_required

logger = logging.getLogger(__name__)

from django.utils import timezone

logger = logging.getLogger(__name__)

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        response = login_user(username, password)
        datos = json.loads(response.content)
        message = datos.get("message")
        user_name = get_logged_user(response)
        #full_name = datos.get("full_name")
        erp_sid = hashlib.sha256(user_name.encode()).hexdigest()
        if message == "Logged In":
            return guardar_sessionid(request, erp_sid, user_name)
        else:
            messages.error(request, "Credenciales inválidas")
    return render(request, "login.html", {"form": form})


# TODO Rename this here and in `login_view`
def guardar_sessionid(request, erp_sid, user_name):
    request.session["erp_session"] = True
    request.session["erp_sid"] = erp_sid
    request.session["username"] = user_name
    request.session["last_activity"] = timezone.now().timestamp()
    request.session.save()
    request.user = ERPUser(erp_sid, user_name, erp_sid, [])
    response_redirect = redirect("home")
    response_redirect.set_cookie(
        key=settings.SESSION_COOKIE_NAME,  # "sessionid"
        value=request.session.session_key,
        max_age=settings.SESSION_COOKIE_AGE,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        samesite=settings.SESSION_COOKIE_SAMESITE,
    )
    return response_redirect

@session_required(url_name="login")
def base_view(request):
    # Usar .get() evita fallos si por alguna razón la clave no existiera
    username = request.session.get("username", "Anónimo")
    logger.info(f"{username} -> base_view")
    return render(request, "inicio.html")

def logout_view(request):
    try:
        logger.info(f"{request.session["username"]}-> logout_view")
        sid = request.session.get("erp_session")
        get_logout(sid)
        request.session.flush()  # elimina toda la sesión
    except KeyError as e:   
        logger.warning( f"No existe 'username' en la sesión. " f"Session Key: {request.session.session_key}. " f"Error: {e}" ) 
        request.session.flush()  
    return redirect("login")

def csrf_failure(request, reason=""):
    logger.info("csrf_failure")
    return redirect(
        f"{reverse('login')}?next={request.get_full_path()}"
    )