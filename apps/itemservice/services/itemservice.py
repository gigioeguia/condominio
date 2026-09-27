import json
import os, requests
from dotenv import load_dotenv

load_dotenv()

ERP_BASE_URL = os.getenv("ERP_BASE_URL")
ERP_API_KEY = os.getenv("ERP_API_KEY")
ERP_APISECRET = os.getenv("ERP_APISECRET")
LOGIN_URL = f"{ERP_BASE_URL}/api/method/login"

HEADERS = {
    "Authorization": f"token {ERP_API_KEY}:{ERP_APISECRET}",
    "Content-Type": "application/json",
    "Cookie": f"sid={os.getenv('ERP_SESSION_ID')}",
    "Accept": "application/json",
}

def _get_resource(resource, filters=None, fields=None):
    url = f"{ERP_BASE_URL}/api/resource/{resource}"
    params = {
        "filters": json.dumps(filters or []),
        "fields": json.dumps(fields or ["name"]),
        "limit_page_length": 0,
    }
    return requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )

def is_servicio(item_group_name):
    return _get_resource("Item Group",
            [["item_group_name","=",item_group_name],["is_group","=",0],["docstatus","=",0]],
            ["item_group_name"])


def add_servicio(item_group_name):
    url = f"{ERP_BASE_URL}/api/resource/Item Group"
    data = {
        "item_group_name": item_group_name,
        "parent_item_group": "All Item Groups",
        "is_group": 0
    }
    return requests.post(url, headers=HEADERS, json=data, timeout=30, allow_redirects=False,)

def get_item_by_item_code(item_code,item_group_name):
    return _get_resource("Item",
            [["item_code","=",item_code],["item_group","=",item_group_name],["disabled","=",0]],
            ["item_code","item_name","description","is_sales_item","is_purchase_item"])
    

def get_price_by_item_code(item_code):
    return _get_resource("Item Price",
            [["item_code","=",item_code],["docstatus","=",0]],
            ["name","item_code","price_list_rate","currency"])

def get_price_list():
    return _get_resource("Item Price",
            [["docstatus","=",0]],
            ["item_code","item_name","currency","price_list_rate","valid_from"])    

def get_itemservices_list():
    return _get_resource("Item",
            [["docstatus","=",0]],
            ["name","item_code","item_name","item_group","standard_rate"])    

def add_item_code_service(data):
    url = f"{ERP_BASE_URL}/api/resource/Item"
    return requests.post(url, headers=HEADERS, json=data)

def update_item_code_service(data,item_code):
    url = f"{ERP_BASE_URL}/api/resource/Item/{item_code}"
    return requests.put(url, headers=HEADERS, json=data)

def add_item_code_price(data):
    url = f"{ERP_BASE_URL}/api/resource/Item Price"
    return requests.post(url, headers=HEADERS, json=data)
    
def update_item_code_price(data):
    url = f"{ERP_BASE_URL}/api/resource/Item Price/{data["name_price"]}"
    return requests.put(url, headers=HEADERS, json=data)
