import json
import os
from django.urls import reverse
import pandas as pd
import requests
import re
import logging

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET
from django_tables2 import RequestConfig
from django_tables2.export import TableExport
from .table import OrganizationTable
from .form import ImportJsonForm, OrganizationForm, OrganizationImportForm, OrganizationFilterForm, CatalogoCuentasForm
from config.utils import agregar_atributos, getRequestException, agregar_data_Tab, obtener_mensaje_erpnext, procesar_acount_json, \
    obtener_plan_acounts, serialize_dates
from .services import get_organizations, search_resource, get_chart_acount_for_country, get_company_by_name, saveCompany, get_imprimir, \
    get_account, get_value_field, update_fiedl_company 
from config.decorators import session_required

logger = logging.getLogger(__name__)


@require_GET
def get_detalle(request, name):
    logger.info("get_detalle")
    response = get_company_by_name(name)
    data = response.json()
    return JsonResponse(data["data"])
        
def _read_organization_import_file(archivo):
    logger.info("read_organization_import_file")
    extension = os.path.splitext(archivo.name)[1].lower()
    archivo.seek(0)
    if extension == ".csv":
        return pd.read_csv(archivo)
    if extension in [".xlsx", ".xls"]:
        return pd.read_excel(archivo)
    raise ValueError("Formato de archivo no soportado.")

@session_required("login")
@require_GET
def get_chart_templates(request):
    try:
        logger.info(f"{request.session["username"]}-> get_chart_templates")
        data_param = request.GET.get("dataParam", "{}")
        data = json.loads(data_param)
        country = data.get("country")
        response = get_chart_acount_for_country( request, country )
        data = response.json()
        
        charts = data.get("message", [])
        search = request.GET.get("term", "").strip()
        patron = re.compile(rf".*{search}.*", re.IGNORECASE)
        chartsRest = [s for s in charts if patron.match(s)]

        results = [{"id": item, "text": item} for item in chartsRest]
        
        return JsonResponse({"results": results})
    except requests.RequestException:
        getRequestException("No fue posible consultar los paises en backend.", 502, logger)

@session_required("login")
@require_GET
def get_countries(request):
    try:
        logger.info(f"{request.session["username"]}-> get_countries")
        response = search_resource(request=request, resource="Country", fields=["name", "code"],)
        response.raise_for_status()
        payload = response.json()
        countries = payload.get("data", [])
        results = [
            {
                "id": country["name"],
                "text": f'{country["name"]}',
            }
            for country in countries
                if country.get("enabled", 1)
        ]
        return JsonResponse({"results": results})
    except requests.exceptions.RequestException as error:
        getRequestException(f"Error consultando backend: {str(error)}", 502, logger)
    except ValueError as error:
        getRequestException(f"Respuesta JSON inválida: {str(error)}", 502, logger)
    except requests.RequestException:
        getRequestException("No fue posible consultar los paises en backend.", 502, logger)
        
@session_required("login")
@require_GET
def get_currencies(request):
    try:
        logger.info(f"{request.session["username"]}-> get_currencies")   
        response = search_resource(request=request, resource="Currency", fields=["name", "enabled"],)
        response.raise_for_status()
        currencies = response.json().get("data", [])
        results = [
            {
                "id": currency["name"],
                "text": f'{currency["name"]}',
            }
            for currency in currencies
                if currency.get("enabled", 1)
        ]
        return JsonResponse({"results": results})
        
    except requests.RequestException:
        getRequestException("No fue posible consultar las monedas en backend.",404,logger)


@session_required("login")
def compania(request,name=None):
    logger.info(f"{request.session["username"]}-> Agregar / modificar compañia")
    request.session["companyName"] = name
    request.session.modified = True
    request.session.save()
    breadcrumbs = [
        { "label": "Organizaciones", "url": "organization:list", },
        { "label": "Compania Detalles", "url": None, }
    ]
    context = {}
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            try:
                result = save_company_data(request, form.cleaned_data)
                return procesar_resultado_empresa(request, result)
            except json.JSONDecodeError:
                form.add_error("text", "El contenido no es un JSON válido.")
    elif name:
        breadcrumbs.append( { "label": f"{name}", "url": None, })
        resp = get_company_by_name(name);
        if resp.status_code != 200:
            getRequestException(f"Error al consultar compañía: {resp.text}", resp.status_code, logger)
        data = resp.json()
        company = data["data"]
        context = agregar_atributos(context, "action", 1)
        context = agregar_atributos(context, "disabled_tab", "0")
        company["action"]=1
        form = OrganizationForm(initial=company)   
        form.fields["company_name"].widget.attrs["readonly"] = True
        form.fields["abbr"].widget.attrs["readonly"] = True
    else:
        context = agregar_atributos({}, "action", 0)
        context = agregar_atributos(context, "disabled_tab", "1")
        form = OrganizationForm()
    context = agregar_atributos(context, "breadcrumbs", breadcrumbs)
    context = agregar_data_Tab("company_options.json", context)
    context = agregar_atributos(context,"active_tab","compania")
    context = agregar_atributos(context,"name",name)
    context = agregar_atributos(context,"form",form)
    return render(
        request,
        "organization/compania.html",
        context,
    )    
    
@session_required("login")
def companias_list(request):
    logger.info(f"{request.session["username"]}-> organization_list")
    error_message = None
    organizations = []
    breadcrumbs = [ { "label": "Organizaciones", "url": None, } ]
    context = agregar_atributos( {}, "breadcrumbs", breadcrumbs, )
    try:
        response = get_organizations()
        response.raise_for_status()
        result = response.json()
        organizations = result.get("data", [])
        if not isinstance(organizations, list):
            error_message = (
                "La API devolvió un formato de datos inválido."
            )
    except requests.RequestException as error:
        error_message = f"No fue posible consultar la API: {error}"
    except ValueError as error:
        error_message = f"La API devolvió un JSON inválido: {error}"
    form = OrganizationFilterForm(request.GET or None)
    if form.is_valid():
        name = form.cleaned_data.get("name", "").strip().lower()
        abbr = form.cleaned_data.get("abbr", "").strip().lower()
        country = form.cleaned_data.get("country", "").strip().lower()
        if name:
            organizations = [
                organization
                for organization in organizations
                if name in str(
                    organization.get("name", "")
                ).lower()
            ]
        if abbr:
            organizations = [
                organization
                for organization in organizations
                if abbr in str(
                    organization.get("abbr", "")
                ).lower()
            ]
        if country:
            organizations = [
                organization
                for organization in organizations
                if country in str(
                    organization.get("country", "")
                ).lower()
            ]
    table = OrganizationTable(organizations)
    RequestConfig(
        request,
        paginate={"per_page": 10},
    ).configure(table)
    filters = {
        "name": request.GET.get("name", ""),
        "abbr": request.GET.get("abbr", ""),
        "country": request.GET.get("country", ""),
    }
    context = agregar_atributos(context, "form", form)
    context = agregar_atributos(
        context,
        "error_message",
        error_message,
    )
    context = agregar_atributos(context, "table", table)
    context = agregar_atributos(context, "filters", filters)
    if request.GET.get("_export") == "xlsx":
        export = TableExport("xlsx", table=table)
        return export.response(
            filename="organizaciones.xlsx"
        )
    if request.GET.get("_export") == "csv":
        export = TableExport("csv", table=table)
        return export.response(
            filename="organizaciones.csv"
        )
    return render(
        request,
        "organization/companias.html",
        context,
    )
    
@session_required("login")
def delete(request, name):
    logger.info(f"{request.session["username"]}-> delete")
    try:
        data = {"company_name": name}
        response = saveCompany("delete", data)
        respuesta_erpnext = response.json()
    except ValueError:
        respuesta_erpnext = {
            "detalle": response.text,
    }
    
    if response.status_code not in [200, 202]:
        exception = respuesta_erpnext["exception"]
        mensaje = exception.replace("frappe.exceptions.LinkExistsError:", "") 
        patron = r"</?a(?:\s[^>]*)?>"
        mensaje = re.sub(patron, "", mensaje, flags=re.IGNORECASE)
        messages.error( request, mensaje )
    else: # response.status_code in [200, 202]: 
        mensaje = f"Se elimino la empresa de forma correct: {name}"
        messages.success( request, mensaje )   
       
    return redirect("organization:list")  

@session_required("login")
def save_company_data(request, company_data=None):
    logger.info(f"{request.session["username"]}-> save_company_data")
    data = serialize_dates(company_data)
    if int(data["action"]) == 1:
        response = saveCompany("put", data)
    if int(data["action"]) == 0:
        response = saveCompany("post", data)
    mensaje = obtener_mensaje_erpnext(response.text)
    resultado = agregar_atributos({}, "status_code", response.status_code)
    if response.status_code != 200:
        resultado = agregar_atributos(resultado, "mensaje", mensaje)  
        return resultado    

    resultado = agregar_atributos(resultado, "status_code", response.text)
    return resultado

@session_required("login")
def organization_import_file(request):
    logger.info(f"{request.session["username"]}-> organization_import_file")
    breadcrumbs = [
        {
            "label": "Organizaciones",
            "url": "organization:list",
        },
        {
            "label": "Importar Organización",
            "url": None,
        },
    ]
    context = {}
    context = agregar_atributos(context, "breadcrumbs", breadcrumbs)
    
    if request.method == "POST":
        form = OrganizationImportForm(request.POST, request.FILES)
    
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            archivo.seek(0)
            dataframe = _read_organization_import_file(archivo)
            organization = {}
            for _, fila in dataframe.iterrows():
                organization = agregar_atributos(organization, "company_name", fila["company_name"])
                organization = agregar_atributos(organization, "abbr", fila["abbr"])
                organization = agregar_atributos(organization, "default_currency", fila["default_currency"])
                organization = agregar_atributos(organization, "tax_id", fila["tax_id"])
                organization = agregar_atributos(organization, "country", fila["country"])
                organization = agregar_atributos(organization, "domain", fila["domain"])
                organization = agregar_atributos(organization, "date_of_establishment", fila["date_of_establishment"])
                organization = agregar_atributos(organization, "date_of_incorporation", fila["date_of_incorporation"])
                
                organization = agregar_atributos(organization, "date_of_commencement", fila["date_of_commencement"])
                organization = agregar_atributos(organization, "phone_no", fila["phone_no"])
                organization = agregar_atributos(organization, "fax", fila["fax"])
                organization = agregar_atributos(organization, "email", fila["email"])
                organization = agregar_atributos(organization, "company_description", fila["company_description"])
                
                organization = agregar_atributos(organization, "website", fila["website"])
                organization = agregar_atributos(organization, "registration_details", fila["registration_details"])
                organization = agregar_atributos(organization, "chart_of_accounts", fila["chart_of_accounts"])
                organization = agregar_atributos(organization, "create_chart_of_accounts_based_on", fila["create_chart_of_accounts_based_on"])
                organization = agregar_atributos(organization, "action", 0)
            result = save_company_data(request, organization)
            return procesar_resultado_empresa(request, result)
    else:
        form = OrganizationImportForm()
    
    context = agregar_atributos(context, "form", form)
    context = agregar_atributos(context, "active_tab", "file")
    context = agregar_atributos(context, "disabled_tab", "0")
    context = agregar_data_Tab("import_options.json", context)
    return render(
        request,
        "organization/import_file.html",
        context,
    )

@session_required("login") 
def organization_import_json(request):
    logger.info(f"{request.session["username"]}-> organization_import_json")
    breadcrumbs = [
            {
                "label": "Organizaciones",
                "url": "organization:list",
            },
            {
                "label": "Importar Organización",
                "url": None,
            },
        ]
    context = {}
    context = agregar_atributos(context, "breadcrumbs", breadcrumbs)
    context = agregar_atributos(context, "active_tab", "json")
    context = agregar_atributos(context, "disabled_tab","0")
    context = agregar_data_Tab("import_options.json", context)
    
    if request.method == "POST":
        form = ImportJsonForm(request.POST)
        if form.is_valid():
            try:
                organization = json.loads(form.cleaned_data["text"])
                organization["action"]=0
                result = save_company_data(request, organization)
                return procesar_resultado_empresa(request, result)
            except json.JSONDecodeError:
                form.add_error("text", "El contenido no es un JSON válido.")
    else:
        form = ImportJsonForm()
    context = agregar_atributos(context,"form", form)
    return render(
        request,
        "organization/import_json.html",
        context,
    )

# --- Helpers ---
def validar_cuentas(campos_final, datosf):
    acount_no_existe, acount_si_existe = [], []
    for campo in campos_final:
        strAcountName = datosf.get(campo)
        response = get_account(strAcountName)
        if response.status_code != 200:
            logger.error("Error HTTP get_account: %s %s", response.status_code, response.text)
            continue
        acount = response.json().get("data")
        target_list = acount_si_existe if acount else acount_no_existe
        target_list.append({"field": campo, "value": strAcountName})
    return acount_no_existe, acount_si_existe


def comparar_valores(company_name, cuentas):
    acount_save_field = []
    for acountForm in cuentas:
        response = get_value_field(company_name, acountForm["field"])
        if response.status_code != 200:
            logger.error("Error HTTP get_value_field: %s %s", response.status_code, response.text)
            continue
        result = response.json().get("data")
        valorOld = result[0].get(acountForm["field"])
        valorNew = acountForm["value"]
        if valorOld != valorNew:
            acount_save_field.append(acountForm)
    return acount_save_field


def guardar_cambios(company_name, cuentas):
    result_save_field = []
    for field in cuentas:
        response = update_fiedl_company(field, company_name)
        if response.status_code != 200:
            logger.error("Error HTTP update_field_company: %s %s", response.status_code, response.text)
            continue
        result_save_field.append(response.json().get("data"))
    return result_save_field


# --- Vista principal ---
@session_required("login")
def catalogo_cuentas(request):
    logger.info(f"{request.session.get('username')} -> Agregar / modificar compañía")

    breadcrumbs = [
        {"label": "Organizaciones", "url": "organization:list"},
        {"label": "Compañía Detalles", "url": None},
        {"label": "Catálogo de cuentas", "url": None},
    ]
    context = agregar_atributos({}, "breadcrumbs", breadcrumbs)
    context = agregar_data_Tab("company_options.json", context)
    context = agregar_atributos(context, "active_tab", "acount")

    if request.method == "POST":
        form = CatalogoCuentasForm(request.POST)
        if form.is_valid():
            datosf = form.cleaned_data
            campos_excluir = {
                "abbr",
                "company_name",
                "currency",
                "crear_plan_basado_en",
                "plantilla_catalogo",
            }
            campos_final = [
                campo
                for campo, valor in datosf.items()
                if valor and campo not in campos_excluir
            ]

            company_name = datosf.get("company_name")
            acount_no_existe, acount_si_existe = validar_cuentas(
                campos_final,
                datosf,
            )
            cuentas_validar = acount_si_existe + acount_no_existe
            acount_save_field = comparar_valores(
                company_name,
                cuentas_validar,
            )
            result_save_field = guardar_cambios(
                company_name,
                acount_save_field,
            )

            if result_save_field:
                messages.success(request, f"{result_save_field}")

            logger.info("Cuentas no existentes: %s", acount_no_existe)
            logger.info("Cuentas existentes: %s", acount_si_existe)
            logger.info("Cuentas a guardar: %s", acount_save_field)
            logger.info("Resultados guardados: %s", result_save_field)
            return redirect("organization:catalogo_cuentas")
    else:
        company_name = request.session.get("companyName")
        response = get_company_by_name(company_name)
        company = response.json().get("data", {})
        form = CatalogoCuentasForm(initial={
            "abbr": company.get("abbr", ""),
            "company_name": company.get("company_name", ""),
            "currency": company.get("default_currency", ""),
            "crear_plan_basado_en": company.get("create_chart_of_accounts_based_on", ""),
            "plantilla_catalogo": company.get("chart_of_accounts", ""),
            "default_cash_account": company.get("default_cash_account", ""),
            "default_bank_account": company.get("default_bank_account", ""),
            "default_expense_account": company.get("default_expense_account", ""),
            "default_income_account": company.get("default_income_account", ""),
            "default_receivable_account": company.get("default_receivable_account", ""),
            "default_payable_account": company.get("default_payable_account", ""),
            "cost_center": company.get("cost_center", ""),
            "default_inventory_account": company.get("default_inventory_account", ""),
            "accumulated_depreciation_account": company.get("accumulated_depreciation_account", ""),
            "depreciation_expense_account": company.get("depreciation_expense_account", ""),
            "stock_adjustment_account": company.get("stock_adjustment_account", ""),
            "stock_received_but_not_billed": company.get("stock_received_but_not_billed", ""),
            "valuation_method": company.get("valuation_method", ""),
            "default_discount_account": company.get("default_discount_account", ""),
            "write_off_account": company.get("write_off_account", ""),
            "unrealized_profit_loss_account": company.get("unrealized_profit_loss_account", ""),
            "exchange_gain_loss_account": company.get("exchange_gain_loss_account", ""),
            "unrealized_exchange_gain_loss_account": company.get("unrealized_exchange_gain_loss_account", "")
        })
        form.fields["crear_plan_basado_en"].widget.attrs["readonly"] = True
        form.fields["plantilla_catalogo"].widget.attrs["readonly"] = True

    context = agregar_atributos(context, "form", form)
    return render(request, "organization/accounts.html", context)
    
def procesar_save_acounts(account_data_chart):
    print(f"1- account_data_chart {len(account_data_chart)}")
    account_data_chart = [a for a in account_data_chart if a is not None]
    print(f"2- account_data_chart {len(account_data_chart)}")    
    print(f"account_data_chart {account_data_chart}")
    return None
      

def company_cuentas(request):
    company_name = request.session.get('companyName')
    if not company_name:
        return redirect('inicio')
    return redirect(
        'organization:compania',
        name=company_name
    )

@session_required("login")    
def imprimir(request, name):
    try:
        response = get_imprimir(name)
        response.raise_for_status()
    
        if response.status_code != 200:
            logger.error(f"Error ERPNext: {response.text}")
            return HttpResponse(
                "No fue posible generar el documento.",
                status=500,
                content_type="text/plain",
            )
        else:
            with open("empresa.pdf", "wb") as archivo:
                archivo.write(response.content)

            django_response = HttpResponse( response.content, content_type="application/pdf", ) 
            django_response["Content-Disposition"] = ( f'inline; filename="{name}.pdf"' ) 
            
            return django_response
    
    except requests.RequestException as e:
        logger.exception(f"Error comunicando con ERPNext: {e}")
        return HttpResponse("Error comunicando con ERPNext.", status=502, content_type="text/plain")
    except Exception as e:
        logger.exception(f"Error generando PDF de {name}: {e}")
        return HttpResponse("Error interno generando el documento.", status=500, content_type="text/plain")

def procesar_resultado_empresa(request, result):
    if result.get("session_expired"):
        messages.error(
            request,
            "La sesión de ERPNext expiró. Vuelve a iniciar sesión."
        )
        return redirect("organization:list")

    status_code = result.get("status_code")

    if status_code == 200:
        messages.success(
            request,
            "El archivo fue cargado correctamente."
        )
        return redirect("organization:list")

    mensaje = result.get("mensaje") or result.get("exception") or "La empresa fue guardada correctamente."

    messages.success(request, mensaje)

    return redirect("organization:list")    