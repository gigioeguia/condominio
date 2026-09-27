import logging
from datetime import datetime
from config.decorators import session_required
from django.shortcuts import render
from django.utils.html import strip_tags
from config.utils import add_properties

from ..tables.itemservice import ItemPriceTable

from ..services.itemservice import get_price_list, is_servicio, add_servicio, get_item_by_item_code, get_price_by_item_code
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
    data = response.json().get("data", [])
    result_item_group_name = data[0]["item_group_name"]
    if not result_item_group_name:
        response = add_servicio(item_group_name)

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

def itemservice_form(request,item_code):
    logger.info("itemservice_form")

    context = add_properties({},"breadcrumbs", _breadcrumbs())

    if request.method == "POST":
        form = ItemServiceForm(request.POST)
        print(f"save form {form}")
    elif item_code == 0:
        context["breadcrumbs"].append({ "label": "Agregar", "url": None, })
        form = ItemServiceForm()
    else:
        form = _get_values_update_item(context, item_code)
    
    form.fields["currency"].widget.attrs["readonly"] = True
    form.fields["stock_uom"].widget.attrs["disabled"] = True    
    context = add_properties(context,"form", form)

    return render(
        request,
        "itemservice/itemform.html",
        context
    )        


      
    
   