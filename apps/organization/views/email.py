from django.urls import reverse
import pandas as pd
import logging

from django.contrib import messages
from django.shortcuts import render, redirect

from ..forms.email import EmailAccountForm 
from ..services.email import save_email, get_email_datails

from config.utils import add_properties, agregar_data_Tab
from config.decorators import session_required

logger = logging.getLogger(__name__)
    
@session_required("login") 
def email_create_update(request,name=None):    
    name = request.session.get("companyName", "") if name is None else name
    username = request.session.get("username", "")
    logger.info(
        "%s -> organization_import_json",
        username,
    )
    context = add_properties({},"breadcrumbs", _email_breadcrumbs(name, name))
    context = agregar_data_Tab("company_options.json", context)
    context = add_properties(context, "active_tab", "email")
    if request.method == "POST":
        form = EmailAccountForm(request.POST,company=name)
        if form.is_valid():
            try:
                payload = _build_email_payload(form)
                response = save_email_account(payload)
            except Exception as exc:
                form.add_error(
                    None,
                    f"No fue posible guardar la cuenta de correo: {exc}",
                )
            else:
                action = "actualizó" if name else "creó"
                messages.success(
                    request,
                    f"La cuenta de correo se {action} correctamente.",
                )
                return redirect("organization:company_email")
    elif name is not None:
        response = get_email_datails(name,name)
        result = response.json()
        data = result.get("data", [])
        email_data = data[0]
        form = EmailAccountForm(
            initial={
                "email_id": email_data.get("email_id"),
                "login_id": email_data.get("login_id"),
                "company": email_data.get("company"),
                "service": email_data.get("service"),
                "enable_incoming": email_data.get("enable_incoming"),
                "enable_outgoing": email_data.get("enable_outgoing"),
                "email_account_name": email_data.get("email_account_name"),
                "password": email_data.get("password"),
                "auth_method": email_data.get("auth_method"),
                "ascii_encode_password": email_data.get(
                    "ascii_encode_password",
                    0,
                ),
            },
        )
    else:
        form = EmailAccountForm(company=name)
    context = add_properties(context,"form",form)
    return render(
        request,
        "organization/email_form.html",
        context
    )  

def save_email_account(payload):
    response = save_email(payload)
    response.raise_for_status()
    return response.json()

def _email_breadcrumbs(company, name):
    breadcrumbs = [ 
        { "label": "Organizaciones", "url": "organization:list", }, 
        { "label": "Compañía Detalles", "url": "organization:company_cuentas", }, 
        { "label": "Email Organización", "url": "organization:company_email", }, 
        { "label": company, "url": None, }, ]
    if name: 
        breadcrumbs.append( { "label": name, "url": None, } ) 
    return breadcrumbs

def _build_email_payload(form):
    try:
        cleaned_data = form.cleaned_data
        integer_fields = (
            "enable_incoming",
            "enable_outgoing",
            "awaiting_password",
            "use_ascii_for_password",
        )
        payload = {
            "email_id": cleaned_data["email_id"],
            "service": cleaned_data["service"],
            "company": cleaned_data["company"],
            "domain": cleaned_data["domain"],
            "email_account_name": cleaned_data["email_account_name"],
            "authentication_method": cleaned_data["authentication_method"],
            "email_login": cleaned_data["email_id"],
            "password": cleaned_data["password"],
        }
        payload.update(
            {
                field: int(cleaned_data[field])
                for field in integer_fields
            }
        )
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")    
    return payload