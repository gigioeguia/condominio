import logging
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .services import login_user, get_logout
from .forms import LoginForm
from config.decorators import session_required

logger = logging.getLogger(__name__)

from django.contrib.auth import authenticate, login
from django.utils import timezone
import datetime

logger = logging.getLogger(__name__)

def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]

        # Autenticación con tu backend
        from apps.login.backends import ERPNextBackend
        user = ERPNextBackend().authenticate(request, username=username, password=password)
        if user:
            login(request, user)  # 🔑 genera sessionid sin DB
            request.session["erp_session"] = True
            request.session["erp_sid"] = user.erp_sid
            request.session["username"] = username
            request.session["last_activity"] = timezone.now().timestamp()
            return redirect("home")
        else:
            messages.error(request, "Credenciales inválidas")

    return render(request, "login.html", {"form": form})

@session_required("login")
def base_view(request):
    logger.info(f"{request.session["username"]}-> base_view")
    if "erp_session" not in request.session:
        return redirect("login") 
    return render(request, "inicio.html")

def logout_view(request):
    logger.info(f"{request.session["username"]}-> logout_view")
    sid = request.session.get("erp_session")
    get_logout(sid)
    request.session.flush()  # elimina toda la sesión
    return redirect("login")

def csrf_failure(request, reason=""):
    logger.info("csrf_failure")
    return redirect(
        f"{reverse('login')}?next={request.get_full_path()}"
    )