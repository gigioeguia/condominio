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

CUSTOMER_TYPE_MAP = {
    "Individual": "Persona Física (Individual)",
    "Company": "Empresa / Persona Moral",
    "Proprietorship": "Propietario Único",
    "Partnership": "Sociedad / Asociación",
}
def choicesCustomerType():
    try:
        url = f"{ERP_BASE_URL}/api/resource/DocType/Customer"
        response = requests.get(url, headers=HEADERS, timeout=5)
        response.raise_for_status()
        fields = response.json().get("data", {}).get("fields", [])
        type_field = next((f for f in fields if f.get("fieldname") == "customer_type"), None)
        if not type_field or not type_field.get("options"):
            return []
        return [
            (opt, CUSTOMER_TYPE_MAP.get(opt, opt))
            for line in type_field["options"].split("\n")
            if (opt := line.strip())
        ]
    except requests.RequestException as e:
        return []

CUSTOMER_GROUP_MAP = {
    "Commercial": "Comercial",
    "Government": "Gobierno",
    "Individual": "Individual",
    "Non Profit": "Sin fines de lucro",
}
def choicesCustomerGroup():
    try:
        response = _get_resource("Customer Group", 
                            filters=[["old_parent","=","All Customer Groups"],["is_group","=",0],["docstatus","=",0]], 
                            fields=["name","customer_group_name"])
        response.raise_for_status()
        data = response.json().get("data", {})
        return [ ( item["name"], 
                   CUSTOMER_GROUP_MAP.get(item["customer_group_name"], item["customer_group_name"])) for item in data ]
    except Exception as e:
        return []

TERRITROY_MAP = {
    "Mexico": "Mexíco",
    "Rest Of The World": "Resto del munto"
}
def choicesTerritory():
    try:
        response = _get_resource("Territory", 
                            filters=[["old_parent","=","All Territories"],["is_group","=",0],["docstatus","=",0]], 
                            fields=["name","territory_name"])
        response.raise_for_status()
        data = response.json().get("data", {})
        return [ ( item["name"], 
                           TERRITROY_MAP.get(item["territory_name"], item["territory_name"])) for item in data ]
    except Exception as e:
            return []

def get_detail_condominio(customer_primary_contact):
    return _get_resource("Customer",
                         filters=[["customer_primary_contact","=",customer_primary_contact],["docstatus","=", 0]],
                         fields=["customer_primary_contact","name","customer_name","alias","mobile_no","email_id","customer_type","customer_group","territory"])

def add_customer_name(data):
    url= f"{ERP_BASE_URL}/api/resource/Customer"
    return requests.post(url, headers=HEADERS, json=data)
    
def update_customer_name(data):
    customer_name_quote = quote(data.get("name") or data.get("customer_name"), safe="")
    url = f"{ERP_BASE_URL}/api/resource/Customer/{customer_name_quote}"
    request = requests.Request( method="PUT", url=url, headers=HEADERS, json=data,)
    prepared = request.prepare()
    return requests.Session().send(prepared)

def hadContacto(customer_primary_contact):
    encoded_name = quote(customer_primary_contact, safe="")
    url = ( f"{ERP_BASE_URL}/api/resource/Contact/{encoded_name}")
    return requests.get( url, headers=HEADERS, timeout=30 )
    
def update_customer_contact(data,customer_name):
    if not customer_name:
        raise ValueError("El nombre del Contact es obligatorio")
    encoded_name = quote(str(customer_name), safe="")
    url = f"{ERP_BASE_URL}/api/resource/Contact/{encoded_name}"
    response = requests.put( url=url, headers=HEADERS, json=data, timeout=30,)
    response.raise_for_status()
    return response

def list_homeowner():
    try:
        return _get_resource("Customer", 
                            filters=[["disabled","=",0]], 
                            fields=["customer_primary_contact","customer_name", "alias", "disabled", "customer_type", "customer_group", "territory"])
    except Exception as e:
        return []

def delete_customer(customer_name):
    url = f"{ERP_BASE_URL}/api/resource/Customer/{customer_name}"
    return requests.delete( url, headers=HEADERS, timeout=30 ) 