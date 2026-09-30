import logging

from django.contrib import messages
from django.shortcuts import redirect, render
import requests

from config.decorators import session_required
from config.utils import add_properties, get_message_error

from ..forms.homeowner import CondominoForm
from ..services.homeowner import add_customer_name, update_customer_name, get_detail_condominio, list_homeowner, update_customer_contact, \
            hadContacto, delete_customer
from ..tables.homeowner import CustomerTable

logger = logging.getLogger(__name__)

def _breadcrumbs():
    return [ 
        { "label": "Condominos", "url": "homeowner:list", },
    ]  

@session_required("login")
def homeowner_list(request):
    logger.info("itemservice_list")
    context = add_properties({},"breadcrumbs", _breadcrumbs())
    response = list_homeowner()
    response.raise_for_status()
    table = CustomerTable(response.json().get("data", []))
    table = CustomerTable(response.json().get("data", []))
    context = add_properties(context,"table", table)
    return render(
        request,
        "homeowner/homeowners.html",
        context,
    )
    
def _modificar_email_telefono(data):
    response_existe = hadContacto(data.get("customer_primary_contact"))
    response_existe.raise_for_status()
    if response_existe.status_code == 200:
        documento = response_existe.json()["data"]
        payload = {
            "email_ids": [
                {
                    "name": email["name"],
                    "email_id": data["email_id"],
                    "is_primary": email["is_primary"],
                }
                for email in documento.get("email_ids", [])
            ],
            "phone_nos": [
                {
                    "name": phone["name"],
                    "phone": data["mobile_no"],
                    "is_primary_phone": phone.get("is_primary_phone", 0),
                    "is_primary_mobile_no": phone.get("is_primary_mobile_no", 0),
                }
                for phone in documento.get("phone_nos", [])
            ],
        }
        response_email_telefono = update_customer_contact(payload,data.get("customer_primary_contact"))
        if response_email_telefono.status_code == 200:
            logger.info("200- contacto guardado con exito")
        else:
            logger.error(f"{response_email_telefono.status_code} {response_email_telefono.text}")
    return response_email_telefono
    
def save_homeowner(data):
    if data.get("customer_name") is None:
        response_homeowner = add_customer_name(data)
        response_contact_homeowner = None
    else:
        response_contact_homeowner = _modificar_email_telefono(data)
        response_homeowner = update_customer_name(data)
   
    if response_homeowner.status_code != 200:
        return get_message_error(response_homeowner)
    
    if response_contact_homeowner is not None:
        return "No se persistio contacto"

    if response_contact_homeowner.status_code != 200:
        return get_message_error(response_contact_homeowner)
    
    mensajeItem = response_homeowner.json().get("data").get("name")
    return f"Se guardo el homeowner: {mensajeItem}"    
        
def _get_condominio_detail(customer_primary_contact):
    response = get_detail_condominio(customer_primary_contact)
    return response.json().get("data", [])[0]

def homeowner_form_new(request):
    return homeowner_form_update(request, None)
    
def homeowner_form_update(request,customer_primary_contact=None):
    logger.info(f"homeowner_form {customer_primary_contact}")
    context = add_properties({},"breadcrumbs", _breadcrumbs())
    if request.method == "POST":
        form = CondominoForm(request.POST)
        if form.is_valid():
            mensaje = save_homeowner(form.cleaned_data)
            if "Error:" in mensaje:
                messages.error(request, mensaje)
            else:
                messages.success(request, mensaje)
                return redirect("homeowner:list")
    elif customer_primary_contact is None:
        context.get("breadcrumbs", []).append({"label": "Agregar","url": None,})
        form = CondominoForm()
    else:
        homeowner = _get_condominio_detail(customer_primary_contact)        
        context.get("breadcrumbs", []).append({"label": "Modidifcar","url": None,})
        context.get("breadcrumbs", []).append({"label": homeowner.get("customer_name"), "url": None,})
        form = CondominoForm(initial=homeowner)
        form.fields["customer_name"].widget.attrs["readonly"] = True
    context = add_properties(context,"form", form)
    return render(
        request,
        "homeowner/homeownersform.html",
        context,
    )
    
def homeowner_form_delete(request, customer_name):
    respose = delete_customer(customer_name);
    messages.success(request, f"se elimino de forma correct {customer_name}")
    return redirect("homeowner:list")