import contextlib
import json

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings

from datetime import date, datetime

def agregar_atributos(json_data, key, valor):
    json_data[key] = valor
    return json_data

def getRequestException(error, status, logger):
    logger.exception(error)
    return JsonResponse( {
        "results": [],
        "error": error,
        },
        status=status,
    )

def serialize_dates(data):
    if isinstance(data, dict):
        return {
            key: serialize_dates(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [serialize_dates(value) for value in data]
    elif isinstance(data, (date, datetime)):
        return data.isoformat()
    else:
        return data

def agregar_data_Tab(json_filename, context=None):
    component_data = {}
    if context is None:
        context = {}
        
    json_path = settings.BASE_DIR / "static/data" / json_filename

    with json_path.open("r", encoding="utf-8") as file:
        component_data = json.load(file)
    
    context = agregar_atributos(context, "json_filename", json_filename) 
    context = agregar_atributos(context, "component_data", component_data)  
    return context

def obtener_plan_acounts(json_filename):
    component_data = []
    json_path = settings.BASE_DIR / "static/data" / json_filename
    with json_path.open("r", encoding="utf-8") as file:
        component_data = json.load(file)
    return component_data

def obtener_mensaje_erpnext(data):
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            return data or "La respuesta está vacía y no contiene JSON."

    if not isinstance(data, dict):
        return "La respuesta de ERPNext no tiene un formato válido."

    exception = data.get("exception", "")
    if exception:
        return exception.split(": ", 1)[1] if ": " in exception else exception

    return data.get(
        "message",
        "ERPNext no proporcionó un mensaje de error."
    )

def obtener_valor_field(datos,key):
    if key in datos:
        return True, datos[key]
    return False, None 

def reemplazar_abbr(valor, abbr):
    if isinstance(valor, str):
        return valor.replace("abbr", abbr)

    if isinstance(valor, list):
        return [
            reemplazar_abbr(elemento, abbr)
            for elemento in valor
        ]

    if isinstance(valor, dict):
        return {
            clave: reemplazar_abbr(elemento, abbr)
            for clave, elemento in valor.items()
        }

    return valor

def procesar_acount_json(acountNew,account_data_chart):
    for account in account_data_chart:
        existe, valor_field = obtener_valor_field(account, acountNew["claveField"])
        if existe and valor_field == acountNew["valorField"]:
                account = reemplazar_abbr(account, acountNew["abbr"])
                account["account_name"]=acountNew["valorAccountName"]
                account["company"]=acountNew["valorCompany"]
                account["currency"]=acountNew["valorCurrency"]
                return account