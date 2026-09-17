from django.shortcuts import render, redirect
from .decorators import session_required
import logging

logger = logging.getLogger(__name__)

@session_required("login")
def configEmail_view(request):
    logger.info(f"{request.session["username"]}-> configEmail_view")
    if "erp_session" not in request.session:
        return redirect("login") 
    return render(request, "configEmail.html")

@session_required("login")
def condominium_view(request):
    logger.info(f"{request.session["username"]}-> condominium_view")
    if "erp_session" not in request.session:
        return redirect("login") 
    return render(request, "condominium.html")

@session_required("login")
def paymentPlan_view(request):
    logger.info(f"{request.session["username"]}-> paymentPlan_view")
    if "erp_session" not in request.session:
        return redirect("login") 
    return render(request, "paymentPlan.html")

@session_required("login")
def error_view(request):
    logger.info(f"{request.session["username"]}-> error_view")
    return render(request, "error.html", status=400)

