import json
import os
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
from config.utils import agregar_atributos, getRequestException, agregar_data_Tab, obtener_mensaje_erpnext, procesar_acount_json, obtener_plan_acounts
from .services import get_organizations, search_resource, get_chart_acount_for_country, get_company_by_name, saveCompany, get_imprimir
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
    company_name = request.session.get("companyName")
    if not company_name:
        request.session["companyName"] = name
        request.session.modified = True
        company_name = name
    
    breadcrumbs = [
        { "label": "Organizaciones", "url": "organization:list", },
        { "label": "Compania Detalles", "url": None, }
    ]
    company={}
    if company_name:
        breadcrumbs.append( { "label": f"{company_name}", "url": None, })
        resp = get_company_by_name(company_name);
        if resp.status_code != 200:
            getRequestException(f"Error al consultar compañía: {resp.text}", resp.status_code, logger)
        data = resp.json()
        company = data["data"]
        context = agregar_atributos({}, "action", 1)
        context = agregar_atributos(context, "disabled_tab", "0")
    else:
        context = agregar_atributos({}, "action", 0)
        context = agregar_atributos(context, "disabled_tab", "1")
        
    context = agregar_atributos(context, "breadcrumbs", breadcrumbs)
    context = agregar_data_Tab("company_options.json", context)
    context = agregar_atributos(context,"active_tab","compania")
    context = agregar_atributos(context,"name",company_name)
    
    if request.method == "POST":
        form = OrganizationForm(request.POST)
        if form.is_valid():
            try:
                result = save_company_data(request, context["action"] , form.cleaned_data)
                return procesar_resultado_empresa(request, result)
            except json.JSONDecodeError:
                form.add_error("text", "El contenido no es un JSON válido.")
        
    elif company_name:
        form = OrganizationForm(initial=company)   
        form.fields["company_name"].widget.attrs["readonly"] = True
    else:
        form = OrganizationForm()
        
    
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
def save_company_data(request, action=1, company_data=None):
    logger.info(f"{request.session["username"]}-> save_company_data")
    if action == 1:
        response = saveCompany("put", company_data)

    if action == 0:
        response = saveCompany("post", company_data)
    
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
            
            result = save_company_data(request,"Crear", organization)
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
                result = save_company_data(request,"Crear", organization)
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

@session_required("login")
def catalogo_cuentas(request):
    logger.info(f"{request.session["username"]}-> Agregar / modificar compañia")
    breadcrumbs = [
        { "label": "Organizaciones", "url": "organization:list", },
        { "label": "Compania Detalles", "url": None, },
        { "label": "Catalogo de cuentas", "url": None, }
    ]
    context = agregar_atributos({}, "breadcrumbs", breadcrumbs)
    context = agregar_data_Tab("company_options.json", context)
    context = agregar_atributos(context,"active_tab","acount")
    if request.method == "POST":
        form = CatalogoCuentasForm(request.POST)

        if form.is_valid():
            datosf = form.cleaned_data
            strAbbr = datosf.get("abbr")
            strCompany_name = datosf.get("company_name")
            strCurrency = datosf.get("company_name")

            account_data_chart = []
            plan = obtener_plan_acounts("account.json")
            # Definimos las cuentas que queremos procesar
            cuentas = [
                ("cuenta_bancaria", "field", "default_bank_account"),
                ("cuenta_por_cobrar", "field", "default_receivable_account"),
                ("cuenta_por_pagar", "field", "default_payable_account"),
                ("cuenta_costos_venta","field", "default_expense_account"),
                ("cuenta_ingresos","field", "default_income_account"),
                ("cuenta_efectivo","field","default_cash_account")
            ]
            
            for campo_form, key_field, valor_field in cuentas:
                strAcount = datosf.get(campo_form)
                if strAcount:  # solo procesar si hay valor
                    acountNew = {
                        "abbr": strAbbr,
                        "claveField": key_field,
                        "valorField": valor_field,
                        "valorAccountName": strAcount,
                        "valorCompany": strCompany_name,
                        "valorCurrency": strCurrency,
                    }
                    itemAcount = procesar_acount_json(acountNew, plan)
                    account_data_chart.append(itemAcount)
            print(f"account_data_chart {account_data_chart}")
              
            # Guardar los datos en el modelo correspondiente
            # Por ejemplo:
            # CatalogoConfiguracion.objects.create(**datos)

            messages.success(
                request,
                "La configuración del catálogo se guardó correctamente.",
            )
            return redirect("organization:catalogo_cuentas")
    else:
        company_name = request.session.get("companyName")
        response = get_company_by_name(company_name)
        data = response.json()
        company = data["data"]
        form = CatalogoCuentasForm(
            initial={
                "abbr": company["abbr"],
                "company_name": company["company_name"],
                "currency": company["default_currency"],
                "crear_plan_basado_en": company["create_chart_of_accounts_based_on"], #open
                "plantilla_catalogo": company["chart_of_accounts"],
                "cuenta_bancaria": company["default_bank_account"],                   #open  
                "cuenta_costos_venta": company["default_expense_account"],
                "cuenta_efectivo": company["default_cash_account"],
                "cuenta_ingresos": company["default_income_account"],
                "cuenta_por_cobrar": company["default_receivable_account"],           #open
                "cuenta_por_pagar": company["default_payable_account"],               #open
                "centro_costos": company["cost_center"],
                "cuenta_inventarioas": company["default_inventory_account"]
            }
        )
    context = agregar_atributos(context,"form",form)
    return render(
        request,
        "organization/accounts.html",
        context
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