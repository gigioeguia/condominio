import logging
import json

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse


from config.decorators import session_required
from config.utils import add_properties, get_message_error, to_bool

from ..forms.homeowner import CondominoForm
from ..forms.addres import AddressForm
from ..services.homeowner import add_customer_name, update_customer_name, get_detail_condominio, list_homeowner, update_customer_contact, \
            hadContacto, delete_customer
from ..services.addres import get_domicilio_email_mobile_type_customer, add_addres, update_address            
from ..tables.homeowner import CustomerTable

logger = logging.getLogger(__name__)

def _breadcrumbs():
    return [ 
        { "label": "Propiedad", "url": "homeowner:list", },
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
    if data.get("customer_primary_contact") == "":
        response_homeowner = add_customer_name(data)
        response_contact_homeowner = None
    else:
        response_contact_homeowner = _modificar_email_telefono(data)
        response_homeowner = update_customer_name(data)
   
    if response_homeowner.status_code != 200:
        return get_message_error(response_homeowner)
    
    if response_contact_homeowner is not None and response_contact_homeowner.status_code != 200:
        return get_message_error(response_contact_homeowner)
    
    mensajeItem = response_homeowner.json().get("data").get("name")
    return f"Se guardo la propiedad: {mensajeItem}"    
        
def _get_condominio_detail(customer_primary_contact):
    response = get_detail_condominio(customer_primary_contact)
    return response.json().get("data", [])[0]

def homeowner_form_new(request):
    return homeowner_form_update(request, None)

def _get_address_detail_only_string(address_detail):
    if address_detail is None:
        return ""
    address_components = [
        address_detail.get("address_line1", ""),
        address_detail.get("address_line2", ""),
        address_detail.get("city", ""),
        address_detail.get("state", ""),
        address_detail.get("country", ""),
        address_detail.get("pincode", ""),
    ]
    return ", ".join(filter(None, address_components))

def _get_customer_detail_to_agregar(context):
    context.get("breadcrumbs", []).append({"label": "Agregar","url": None,})
    context.get("breadcrumbs", []).append({"label": "Nuevo","url": None,})
    address_url = reverse( "homeowner:address_main_update", 
                    kwargs={
                        "actionDir": "Agregar",
                        "customer_name": "customer_name"
                    },
                )
    return CondominoForm(address_url=address_url, actionDir="Agregar")

def _get_customer_detail_to_update(context, homeowner, address_detail):
    action_dir = "Agregar" if address_detail is None else "Modificar"
    initial = homeowner.copy()   
    if address_detail is not None:
        initial["direccion_principal"] = _get_address_detail_only_string(address_detail)

    address_url = reverse(
        "homeowner:address_main_update",
        kwargs={
            "actionDir": action_dir,
            "customer_name": "customer_name",
        },
    )
    breadcrumbs = context.setdefault("breadcrumbs", [])
    breadcrumbs.extend(
        [
            {"label": "Modificar", "url": None},
            {"label": initial.get("customer_name"), "url": None},
        ]
    )

    form = CondominoForm(
        initial=initial,
        address_url=address_url,
        actionDir=action_dir,
    )
    form.fields["customer_name"].widget.attrs["readonly"] = True
    return form

    
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
        form = _get_customer_detail_to_agregar(context)
    else:
        homeowner = _get_condominio_detail(customer_primary_contact)
        if homeowner:
            address_email_mobile_detail = get_domicilio_email_mobile_type_customer(homeowner.get("customer_name"))
            form = _get_customer_detail_to_update(context, homeowner, address_email_mobile_detail)
        else:
            form = _get_customer_detail_to_agregar(context)
            
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

def _get_detail_addreess_to_update(customer_name, context):
    addres_detail = get_domicilio_email_mobile_type_customer(customer_name)
    customer_primary_contact = addres_detail.get("address_title") + "-" + addres_detail.get("address_title") 
    response_customer = get_detail_condominio(customer_primary_contact)
    customer = response_customer.json().get("data", [])[0]
    addres_detail["email_id"] = customer.get("email_id")
    addres_detail["phone"] = customer.get("mobile_no")
    addres_detail["is_primary_address"] = to_bool( addres_detail.get("is_primary_address") )
    addres_detail["is_shipping_address"] = to_bool( addres_detail.get("is_shipping_address") )
    addres_detail["disabled"] = to_bool( addres_detail.get("disabled") )
    context.get("breadcrumbs", []).append({"label": customer_name,"url": None,})
    return AddressForm(initial=addres_detail)

def save_detalle_address(data,acction):
    data["links"] = [
        {
            "link_doctype": "Customer",
            "link_name": data["address_title"],
        }
    ]
    response = add_addres(data) if acction == "Agregar" else update_address(data)
    if response.status_code != 200:
        print(f"ERROR response.text {response.text}")
    return response.text

    
def address_main_for_homeowner(request,actionDir,customer_name):    
    logger.info(f"homeowner_form {address_main_for_homeowner}")
    context = add_properties({},"breadcrumbs", _breadcrumbs())
    context.get("breadcrumbs", []).append({"label": "Direccion", "url": None,})
    context.get("breadcrumbs", []).append({"label": actionDir, "url": None,})
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            mensaje = save_detalle_address(form.cleaned_data,actionDir)
            if "Error:" in mensaje:
                messages.error(request, mensaje)
            else:
                objeto = json.loads(mensaje)
                link_name = objeto.get('data').get('links')[0].get('link_name')
                mensaje = f"Se guardo la direccion: {link_name}"
                messages.success(request, mensaje)
            return redirect(
                "homeowner:edit",
                customer_primary_contact=f"{link_name}-{link_name}",
            )
    elif actionDir == "Agregar":
        initial = {"address_title":customer_name}
        form = AddressForm(initial=initial)
    else:
        form = _get_detail_addreess_to_update(customer_name, context)
    context = add_properties(context,"form", form)
    return render(
        request,
        "homeowner/addressmainform.html",
        context
    )