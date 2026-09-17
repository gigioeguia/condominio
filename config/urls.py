from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from apps.login.views import base_view
from config.views import configEmail_view, condominium_view, paymentPlan_view, error_view

urlpatterns = [
    #path('admin/', admin.site.urls), #propio de django
    path("admin/", include("apps.login.urls")),
    path("admin/login/", include("apps.login.urls")),
    path("organization/", include("apps.organization.urls")),
    path("home/", base_view, name="home"),
    path("configEmail/", configEmail_view, name="configEmail"),
    path("condominium/", condominium_view, name="condominium"),
    path("paymentPlan/", paymentPlan_view, name="paymentPlan"),
    path("error/", error_view, name="error_page"),
    path('favicon.ico', lambda r: HttpResponse(status=204)),
    path('.well-known/appspecific/com.chrome.devtools.json', lambda r: HttpResponse(status=204)),
]
