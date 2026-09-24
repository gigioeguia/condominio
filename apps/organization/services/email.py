import json
import os, requests
from urllib import parse
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

def get_email_account(company):
    url = f"{ERP_BASE_URL}/api/resource/Email Account"
    filters = [["company","=",company],["docstatus","=",0]]
    fields = ["name","docstatus","email_id","company","email_account_name","enable_incoming","enable_outgoing"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def save_email(payload):
    url = (f"{ERP_BASE_URL}/api/resource/Email Account" )
    return requests.post(url, headers=HEADERS, json=payload, timeout=30, allow_redirects=False,)
  