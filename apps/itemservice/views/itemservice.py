import json
import logging
import requests
from datetime import datetime

from django.contrib import messages
from config.decorators import session_required
from django.views.decorators.http import require_POST
from django.shortcuts import redirect, render
from django.utils.html import strip_tags
from config.utils import add_properties, get_message_error

from ..tables.itemservice import ItemPriceTable

from ..services.itemservice import get_price_list, is_servicio, add_servicio, get_item_by_item_code, get_price_by_item_code, \
                                   add_item_code_service, update_item_code_service, add_item_code_price, update_item_code_price, \
                                   deleteItem    
from ..forms.itemservice import ItemServiceForm

logger = logging.getLogger(__name__)

SERVICIO = "Servicios"

def _breadcrumbs():
    return [ 
        { "label": SERVICIO, "url": "itemservice:list", },
    ]  

def _convertirDate(data):
    for row in data:
        if row.get("valid_from"):
            row["valid_from"] = datetime.strptime(
            row["valid_from"],
            "%Y-%m-%d"
            ).date()
    return data

def _get_item_group(item_group_name):
    response = is_servicio(item_group_name)
    response.raise_for_status()

    body = response.json()
    data = body.get("data") or []
    if not isinstance(data, list) or len(data) == 0:
        return add_servicio(item_group_name)

    item_group = data[0]

    if not isinstance(item_group, dict):
        return add_servicio(item_group_name)

    result_item_group_name = item_group.get("item_group_name")

    if not result_item_group_name:
        return add_servicio(item_group_name)

    return result_item_group_name

def _get_values_update_item(context, item_code):
    context["breadcrumbs"].extend([
        {"label": "Modificar", "url": None},
        {"label": item_code, "url": None},
    ])

    item_response = get_item_by_item_code(item_code, SERVICIO)
    items = item_response.json().get("data", [])

    if not items:
        return ItemServiceForm()

    item = items[0]
    item["description"] = strip_tags(item.get("description", ""))

    price_response = get_price_by_item_code(item_code)
    prices = price_response.json().get("data", [])

    if prices:
        price = prices[0]
        item["price_list_rate"] = price.get("price_list_rate")
        item["currency"] = price.get("currency")
        item["name_price"] = price.get("name")

    form = ItemServiceForm(initial=item)

    form.fields["item_code"].widget.attrs["readonly"] = True    
    return form

@session_required("login")
def itemservice_list(request):
    logger.info("itemservice_list")
    item_group_name = SERVICIO
    
    _get_item_group(item_group_name)
    
    context = add_properties({},"breadcrumbs", _breadcrumbs())
    response = get_price_list()
    response.raise_for_status()
    data = response.json().get("data", [])
    data = _convertirDate(data)
    
    table = ItemPriceTable(data)
    context = add_properties(context,"table", table)
    
    return render(
        request,
        "itemservice/itemservice.html",
        context,
    )

def itemservice_form_new(request):
    return itemservice_form(request,0)

def _persistir_item_service(data_from, item_code):
    try:
        data = {
            "item_code": item_code if item_code != 0 else data_from.get("item_code"),
            "item_name": data_from.get("item_name"),
            "description": data_from.get("description"),
            "item_group": data_from.get("item_group_name"),
            "description": data_from.get("description"),
            "stock_uom": data_from.get("stock_uom"),
            "is_sales_item": data_from.get("is_sales_item"),
            "is_purchase_item": data_from.get("is_purchase_item"),
            "price_list_rate": str(data_from.get("price_list_rate")),
            "currency": data_from.get("currency"),
            "price_list": "Standard Selling",
            "name_price": data_from.get("name_price"),
        }
        return save_item_and_price(item_code, data)
    except requests.exceptions.RequestException as e:
        return f"Error de conexión: {e}"


def save_item_and_price(item_code, data):
    if item_code == 0:
        response_item = add_item_code_service(data)
        response_price = (
            add_item_code_price(data)
            if response_item.status_code == 200
            else None
        )
    else:
        response_item = update_item_code_service(data, item_code)
        response_price = (
            update_item_code_price(data)
            if response_item.status_code == 200
            else None
        )

    if response_item.status_code != 200:
        return get_message_error(response_item)
    
    if response_price is None:
        return "No se persistio precio"

    if response_price.status_code != 200:
        return get_message_error(response_price)
    
    mensajeItem = response_item.json().get("data").get("name")
    mensajePrice = response_price.json().get("data").get("price_list_rate")
    return f"Se guardo el servicio: {mensajeItem} con el precio: ${mensajePrice}"

def itemservice_form(request,item_code):
    logger.info("itemservice_form")

    context = add_properties({},"breadcrumbs", _breadcrumbs())

    if request.method == "POST":
        form = ItemServiceForm(request.POST)
        if form.is_valid():
            mensaje =_persistir_item_service(form.cleaned_data,item_code)
            if "Error:" in mensaje:
                messages.error(request, mensaje)
            else:
                messages.success(request, mensaje)
                return redirect("itemservice:list")
                   
    elif item_code == 0:
        context["breadcrumbs"].append({ "label": "Agregar", "url": None, })
        form = ItemServiceForm()
    else:
        form = _get_values_update_item(context, item_code)
    
    form.fields["currency"].widget.attrs["readonly"] = True
    form.fields["stock_uom"].widget.attrs["readonly"] = True    
    context = add_properties(context,"form", form)

    return render( request, "itemservice/itemform.html", context, )        

@require_POST
def itemservice_delete(request,item_code):
    response = deleteItem(item_code)
    messages.success(request, f"Se elimino correctamente {item_code} {response.json().get("data")}")
    return redirect("itemservice:list")
      
    
   