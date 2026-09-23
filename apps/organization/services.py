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

def get_acounts_type(type, company ):
    url = f"{ERP_BASE_URL}/api/resource/Account"
    filters = [["account_type", "=", type],["company","=",company],["is_group","=",0],["disabled","=",0]]
    fields = ["name","account_name","account_number","company","account_currency","account_type"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def get_acounts_root_type(type, company ):
    url = f"{ERP_BASE_URL}/api/resource/Account"
    filters = [["root_type", "=", type],["company","=",company],["is_group","=",0],["disabled","=",0]]
    fields = ["name","account_name","account_number","company","account_currency","account_type"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def get_plan_pago():
    url= f"{ERP_BASE_URL}/api/resource/Payment Terms Template"
    filters = [["docstatus","=",0]]
    fields = ["name","name"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def get_centro_costo(company):
    url= f"{ERP_BASE_URL}/api/resource/Cost Center"
    filters = [["is_group","=",0],["disabled","=",0],["company","=",company]]
    fields=["name"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)   

def get_libro_finanzas():
    url= f"{ERP_BASE_URL}/api/resource/Finance Book"
    filters = [["docstatus","=",0]]
    fields=["name"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def get_report_type(report_type,company):
    url = f"{ERP_BASE_URL}/api/resource/Account"
    filters = [["report_type", "=", report_type],["company","=",company],["is_group","=",0],["disabled","=",0]]
    fields = ["name","account_name","account_number","company","account_currency","account_type"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)    
       
def get_acounts_type_and_root_type(types,company):
    url = f"{ERP_BASE_URL}/api/resource/Account"
    filters = [["account_type", "=", types[0]], ["root_type","=",types[1]],["company","=",company],["is_group","=",0],["disabled","=",0]]
    fields = ["name","account_name","account_number","company","account_currency","account_type"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields),
        "limit_page_length": 0
    }
    return requests.get(url, headers=HEADERS, params=params)

def saveCompany(method,data):
    response = None
    url = f"{ERP_BASE_URL}/api/resource/Company"
    if method == "put":
        company_encoded = parse.quote(data["company_name"])  
        url += f"/{company_encoded}"
        response = requests.put(url, headers=HEADERS, json=data, timeout=30,)
    elif method == "post":
        response = requests.post(url, headers=HEADERS, json=data, timeout=30, allow_redirects=False,)
    elif method == "delete":
        company_encoded = parse.quote(data["company_name"])
        url += f"/{company_encoded}"
        response = requests.delete(url, headers=HEADERS, json=data, timeout=30)    
    else:
        raise ValueError(f"Método {method} no soportado")    
    return response

def get_value_field(company_name,field):
    url = f"{ERP_BASE_URL}/api/resource/Company"
    filters = [["name", "=", company_name]]
    fields = [f"{field}"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields)
    }
    return requests.get(url, headers=HEADERS, params=params)

def update_fiedl_company(field, company_name):
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
    
def get_company_by_name(name: str):
    url = f"{ERP_BASE_URL}/api/resource/Company/{name}"
    fields = [
            "name",
            "abbr",
            "default_currency",
            "tax_id",
            "country",
            "phone_no",
            "email",
            "website",
            "date_of_establishment",
            "domain"
        ]
    params = {
            "fields": json.dumps(fields)
        }
    return requests.get(url, headers=HEADERS, params=params, timeout=30)

def get_account(nameCuenta):
    url = f"{ERP_BASE_URL}/api/resource/Account"
    filters = [["account_name", "=", nameCuenta]]
    fields = ["name", "account_name", "account_number", "account_type", "root_type", "company", "parent_account"]
    params = {
        "filters": json.dumps(filters),
        "fields": json.dumps(fields)
    }
    return requests.get(url, headers=HEADERS, params=params, timeout=30)

def get_organizations():
    url = f"{ERP_BASE_URL}/api/resource/Company"
    fields = [
        "name",
        "abbr",
        "default_currency",
        "tax_id",
        "country",
        "phone_no",
        "email",
        "website",
        "date_of_establishment"
    ]

    params = {
        "fields": json.dumps(fields)
    }
    return requests.get(url, headers=HEADERS, params=params, timeout=15 )

def get_chart_acount_for_country(request,country):
    url = (
        f"{ERP_BASE_URL}/api/method/"
        "erpnext.accounts.doctype.account.chart_of_accounts."
        "chart_of_accounts.get_charts_for_country"
    )
    params = {
        "country": country,
        "with_standard": 1,
    }
    return requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30
    )

def search_resource(request, resource, fields):
    
    search = request.GET.get("term", "").strip()

    params = {
        "fields": json.dumps(fields),
        "limit_page_length": 0,
        "order_by": "name asc",
    }

    if search:
        filters = [[resource, "name", "like", f"%{search}%"]]
        params["filters"] = json.dumps(filters)

    url = f"{ERP_BASE_URL}/api/resource/{resource}"

    return requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=15,
    )
    
def get_imprimir(company: str):
    url = f"{ERP_BASE_URL}/api/method/frappe.utils.print_format.download_pdf"
    params = {
        "doctype": "Company",
        "name": company,
        "format": "Standard",
        "no_letterhead": 0
    }
    return requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=15,
        )
    
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
    