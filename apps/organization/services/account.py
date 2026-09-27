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
ACCOUNT_FIELDS = [ "name", "account_name", "account_number",
                    "company", "account_currency", "account_type",]

def _get_resource(resource, filters=None, fields=None):
    url = f"{ERP_BASE_URL}/api/resource/{resource}"
    params = {
        "filters": json.dumps(filters or []),
        "fields": json.dumps(fields or ["name"]),
        "limit_page_length": 0,
        }
    return requests.get( url, headers=HEADERS, params=params, timeout=30 )

def _get_accounts(filters):
    return _get_resource( "Account", filters=filters, fields=ACCOUNT_FIELDS,
    )

def get_acounts_type(account_type, company ):
    return _get_accounts([["account_type", "=", account_type], ["company", "=", company],
                        ["is_group", "=", 0], ["disabled", "=", 0], ])

def get_acounts_root_type(root_type, company):
    return _get_accounts([["root_type", "=", root_type], ["company", "=", company],
                        ["is_group", "=", 0], ["disabled", "=", 0], ])

def get_plan_pago():
    return _get_resource( "Payment Terms Template",
        filters=[ ["docstatus", "=", 0], ],
        fields=[ "name", ], )    

def get_centro_costo(company):
    return _get_resource( "Cost Center",
        filters=[ ["is_group", "=", 0], ["disabled", "=", 0], ["company", "=", company], ],
        fields=[ "name", ],)    

def get_libro_finanzas():
    return _get_resource( "Finance Book",
    filters=[ ["docstatus", "=", 0], ],
    fields=[ "name", ], )    

def get_report_type(report_type,company):
    return _get_accounts([ ["report_type", "=", report_type], ["company", "=", company],
                        ["is_group", "=", 0], ["disabled", "=", 0],])
       
def get_acounts_type_and_root_type(types,company):
    return _get_accounts([ ["account_type", "=", types[0]], ["root_type", "=", types[1]],
                        ["company", "=", company], ["is_group", "=", 0], ["disabled", "=", 0], ])

def get_account(account_name):
    return _get_resource( "Account",
        filters=[ ["account_name", "=", account_name], ],
        fields=[ "name", "account_name", "account_number", "account_type", "root_type", "company", "parent_account", ],)

def update_field_company(field, company_name):
    response = get_account(field["value"])
    if response.status_code != 200:
        print("Error HTTP:", response.status_code, response.text)
    data = response.json()
    acount = data.get("data")
    if acount :    
        url = f"{ERP_BASE_URL}/api/resource/Company/{company_name}"
        payload = {
            field["field"]: acount[0].get("name")
        }
        return requests.put(url, headers=HEADERS, json=payload, timeout=30)
    return None

def get_value_field(company_name,field):
    return _get_resource( "Company",
        filters=[ ["name", "=", company_name], ],
        fields=[ field, ], )