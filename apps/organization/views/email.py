import json
import os
from django.urls import reverse
import pandas as pd
import requests
import re
import logging

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from django_tables2 import RequestConfig
from django_tables2.export import TableExport

from ..tables.email import EmailAccountTable
from ..forms.email import EmailAccountForm 
from ..services.email import get_email_account, save_email

from config.utils import agregar_atributos, getRequestException, agregar_data_Tab, obtener_mensaje_erpnext, serialize_dates
from config.decorators import session_required

logger = logging.getLogger(__name__)

@session_required("login") 
def company_email(request):
    username = request.session.get("username", "")
    session_company_name = request.session.get("companyName", "")

    logger.info(
        "%s -> organization_import_json",
        username,
    )

    breadcrumbs = [
        {
            "label": "Organizaciones",
            "url": "organization:list",
        },
        {
            "label": "Compañía Detalles",
            "url": "organization:company_cuentas",
        },
        {
            "label": "Email Organización",
            "url": None,
        },
    ]

    response = get_email_account(session_company_name)
    response.raise_for_status()

    response_json = response.json()
    data = response_json.get("data", [])

    logger.info("Datos recibidos: %s", data)

    table = EmailAccountTable(data)

    RequestConfig(
        request,
        paginate={"per_page": 10},
    ).configure(table)

    logger.info(
        "Número de registros de la tabla: %s",
        len(data),
    )

    # Prueba temporal para comprobar si se genera el HTML

    context = {
        "table": table,
        "breadcrumbs": breadcrumbs,
        "data": data,
    }

    return render(
        request,
        "organization/emails.html",
        context,
    )
    
@session_required("login") 
def email_create_update(request):
    session_company_name = request.session.get("companyName", "")
    breadcrumbs = [
        {
            "label": "Organizaciones",
            "url": "organization:list",
        },
        {
            "label": "Compañía Detalles",
            "url": "organization:company_cuentas",
        },
        {
            "label": "Email Organización",
            "url": None,
        },
        {
            "label": session_company_name,
            "url": None
        }
    ]
    context = agregar_atributos({},"breadcrumbs", breadcrumbs)
    if request.method == "POST":
        form = EmailAccountForm(request.POST)

        if form.is_valid():
            try:
                payload = {
                    "email_id": form.cleaned_data["email_id"],
                    "service": form.cleaned_data["service"],
                    "company": form.cleaned_data["company"],
                    "domain": form.cleaned_data["domain"],
                    "email_account_name": form.cleaned_data[
                        "email_account_name"
                    ],
                    "enable_incoming": int(
                        form.cleaned_data["enable_incoming"]
                    ),
                    "enable_outgoing": int(
                        form.cleaned_data["enable_outgoing"]
                    ),
                    "authentication_method": form.cleaned_data[
                        "authentication_method"
                    ],
                    "email_login": form.cleaned_data["email_login"],
                    "password": form.cleaned_data["password"],
                    "awaiting_password": int(
                        form.cleaned_data["awaiting_password"]
                    ),
                    "use_ascii_for_password": int(
                        form.cleaned_data["use_ascii_for_password"]
                    ),
                }

                # Sustituye esta función por tu cliente actual de ERPNext.
                response = save_email_account(payload)

                messages.success(
                    request,
                    "La cuenta de correo se creó correctamente.",
                )

                return redirect("organization:company_email")

            except Exception as exc:
                form.add_error(
                    None,
                    f"No fue posible crear la cuenta: {exc}",
                )
    else:
        form = EmailAccountForm()
    context = agregar_atributos(context,"form",form)
    return render(
        request,
        "organization/email_form.html",
        context
    )  

def save_email_account(payload):
    response = save_email(payload)
    response.raise_for_status()
    return response.json()