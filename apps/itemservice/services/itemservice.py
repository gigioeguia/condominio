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

def get_price_list():
    url = f"{ERP_BASE_URL}/api/resource/Item Price"
    filters=[["docstatus","=",0]]
    fields=["item_code","item_name","currency","price_list_rate","valid_from"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def get_itemservices_list():
    url = f"{ERP_BASE_URL}/api/resource/Item"
    filters = [["docstatus","=",0]]
    fields = ["name","item_code","item_name","item_group","standard_rate"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)