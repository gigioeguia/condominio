from datetime import datetime
from config.decorators import session_required
from django.shortcuts import render
from config.utils import add_properties

from ..tables.itemservice import ItemPriceTable

from ..services.itemservice import get_price_list

def _breadcrumbs():
    return [ 
        { "label": "Servicios", "url": None, },
    ]  

def _convertirDate(data):
    for row in data:
        if row.get("valid_from"):
            row["valid_from"] = datetime.strptime(
            row["valid_from"],
            "%Y-%m-%d"
            ).date()
    return data

@session_required("login")
def itemservice_list(request):
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
    
def itemservice_form(request):
    return render(
        request,
        "itemservice/itemservice.html",
    )        
    
   