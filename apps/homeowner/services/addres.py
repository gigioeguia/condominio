import json
import os, requests
from dotenv import load_dotenv
from urllib.parse import quote

import urllib

load_dotenv()

ERP_BASE_URL = os.getenv("ERP_BASE_URL")
ERP_API_KEY = os.getenv("ERP_API_KEY")
ERP_APISECRET = os.getenv("ERP_APISECRET")
LOGIN_URL = f"{ERP_BASE_URL}/api/method/login"

HEADERS = {
    "Authorization": f"token {ERP_API_KEY}:{ERP_APISECRET}",
    "Content-Type": "application/json",
#    "Cookie": f"sid={os.getenv('ERP_SESSION_ID')}",
    "Accept": "application/json",
}

def _get_resource(resource, filters=None, fields=None):
    url = f"{ERP_BASE_URL}/api/resource/{resource}"
    params = {
        "filters": json.dumps(filters or []),
        "fields": json.dumps(fields or ["name"]),
        "limit_page_length": 0,
    }
    return requests.get( url, headers=HEADERS, params=params, timeout=30 )

"""So los tipos de dirección que se usan en este modulo, los demás se ignoran"""
ADDRESS_TYPE_LABELS = {
        "Billing": "Facturación",
        "Company": "Compañía",
        "Association": "Asociación",
#        "Shipping": "Envío",
#        "Office": "Oficina",
#        "Personal": "Personal",
#        "Plant": "Planta",
#        "Postal": "Postal",
#        "Shop": "Tienda",
#        "Subsidiary": "Sucursal",
#        "Warehouse": "Almacén",
#        "Current": "Actual",
#        "Permanent": "Permanente",
#        "Other": "Otro",
}

def get_type_address_choices():
    try:
        url = f"{ERP_BASE_URL}/api/resource/DocType/Address"
        params = {
            "fields": json.dumps('["name","fields"]'),
            "filters": json.dumps([["fieldname","=","address_type"]])
        }
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        doc = response.json().get("data", {})
        campo = next(
            (field for field in doc.get("fields", [])
            if field.get("fieldname") == "address_type"),
            None,
        )
        original_choices = [
            (opcion.strip(), opcion.strip())
            for opcion in (campo.get("options") or "").splitlines()
            if opcion.strip()
        ]
        return [
            (value, ADDRESS_TYPE_LABELS.get(value, label))
            for value, label in original_choices
            if value in ADDRESS_TYPE_LABELS
        ]
    except requests.RequestException:
        return []
    
    

def get_domicilio_type_customer(customer_name):
    response = _get_resource("Address",[["Dynamic Link","link_doctype","=","Customer"],["Dynamic Link","link_name","=",customer_name]],["*"])
    print( f"{response.status_code} {response.text}" )
    if response.status_code != 200:
        return {}
    else:
        return response.json().get("data", [])[0] if response.json().get("data") else {}

def add_addres(data):
    url = f"{ERP_BASE_URL}/api/resource/Address"
    return requests.post(url, headers=HEADERS,data=json.dumps(data))

def update_address(data):
    url = f"{ERP_BASE_URL}/api/resource/Address/{data["name"]}"
    return requests.put(url, headers=HEADERS,data=json.dumps(data))
