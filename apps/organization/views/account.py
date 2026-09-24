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
from ..forms.account import CatalogoCuentasForm
from config.utils import agregar_atributos, agregar_data_Tab, getRequestException, obtener_mensaje_erpnext, serialize_dates
from ..services.account import get_acounts_type, get_acounts_root_type, get_plan_pago, get_centro_costo, get_libro_finanzas, get_report_type, \
    get_account, update_fiedl_company, get_value_field
from ..services.company import get_company_by_name    
from config.decorators import session_required

logger = logging.getLogger(__name__)

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

@session_required("login") 
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

@session_required("login") 
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
SELECT_PLACEHOLDER = ("", "Seleccione:")

VALUATION_METHOD_CHOICES = [
    ("FIFO", "FIFO"),
    ("Moving Average", "Precio medio variable"),
    ("LIFO", "LIFO"),
]

def response_data(response):
    """
    Obtiene la lista data de una respuesta de ERPNext.
    """
    try:
        return response.json().get("data", [])
    except (AttributeError, ValueError, TypeError):
        logger.exception("Respuesta inválida recibida desde ERPNext")
        return []

def account_choices(accounts, label_key="name", value_key="name"):
    """
    Convierte cuentas de ERPNext al formato esperado por Django:

        [(valor, etiqueta), ...]

    El valor debe ser normalmente el campo `name` de ERPNext.
    """
    choices = [
        (
            account.get(value_key, ""),
            account.get(label_key, account.get(value_key, "")),
        )
        for account in accounts
        if account.get(value_key)
    ]

    return [SELECT_PLACEHOLDER] + choices

def get_account_type_choices(account_type, company_name):
    response = get_acounts_type(account_type, company_name)
    return account_choices(response_data(response))

def get_root_account_choices(root_type, company_name):
    response = get_acounts_root_type(root_type, company_name)
    return account_choices(response_data(response))

def get_plan_pago_choices():
    response = get_plan_pago()
    plans = response_data(response)

    if not plans:
        return [
            ("", "Solicitar plan de pago al administrador"),
        ]

    return account_choices(plans)

def get_catalogo_choices(company_name):
    """
    Obtiene todas las opciones necesarias para CatalogoCuentasForm.
    """

    choices = {
        "default_bank_account": get_account_type_choices(
            "Bank", company_name
        ),
        "default_cash_account": get_account_type_choices(
            "Cash", company_name
        ),
        "default_payable_account": get_account_type_choices(
            "Payable", company_name
        ),
        "default_receivable_account": get_account_type_choices(
            "Receivable", company_name
        ),
        "default_expense_account": get_root_account_choices(
            "Expense", company_name
        ),
        "write_off_account": get_root_account_choices(
            "Expense", company_name
        ),
        "unrealized_profit_loss_account": get_root_account_choices(
            "Asset", company_name
        ),
        "default_income_account": get_root_account_choices(
            "Income", company_name
        ),
        "default_inventory_account": get_account_type_choices(
            "Stock", company_name
        ),
        "stock_adjustment_account": get_account_type_choices(
            "Stock Adjustment", company_name
        ),
        "stock_received_but_not_billed": get_account_type_choices(
            "Stock Received But Not Billed", company_name
        ),
        "accumulated_depreciation_account": get_account_type_choices(
            "Accumulated Depreciation", company_name
        ),
        "depreciation_expense_account": get_account_type_choices(
            "Depreciation", company_name
        ),
        "payment_terms": get_plan_pago_choices(),
        "valuation_method": VALUATION_METHOD_CHOICES,
    }

    # Cuentas válidas para descuentos: Expense + Income.
    discount_choices = (
        choices["default_expense_account"]
        + choices["default_income_account"]
    )

    # Eliminar duplicados conservando el orden y eliminar el placeholder
    discount_choices = list(dict.fromkeys(discount_choices))
    discount_choices = [
        choice for choice in discount_choices if choice[0]
    ]

    choices["default_discount_account"] = [
        SELECT_PLACEHOLDER,
        *sorted(discount_choices, key=lambda choice: choice[1].lower()),
    ]

    # Centros de costo
    response = get_centro_costo(company_name)
    cost_centers = response_data(response)
    choices["cost_center"] = account_choices(cost_centers)

    # Libros de finanzas
    response = get_libro_finanzas()
    finance_books = response_data(response)
    choices["default_finance_book"] = account_choices(finance_books)

    response = get_report_type("Profit and Loss", company_name)
    exchange_gain_loss = response_data(response)
    choices["exchange_gain_loss_account"] = account_choices(exchange_gain_loss)

    return choices

def apply_form_choices(form, choices):
    """
    Asigna las opciones al formulario.
    """
    for field_name, field_choices in choices.items():
        if field_name in form.fields:
            form.fields[field_name].choices = field_choices

@session_required("login") 
def catalogo_cuentas(request):
    username = request.session.get("username")
    logger.info("%s -> Agregar / modificar compañía", username)

    breadcrumbs = [
        {"label": "Organizaciones", "url": "organization:list"},
        {"label": "Compañía Detalles", "url": "organization:company_cuentas"},
        {"label": "Catálogo de cuentas", "url": None},
    ]

    context = agregar_atributos({}, "breadcrumbs", breadcrumbs)
    context = agregar_data_Tab("company_options.json", context)
    context = agregar_atributos(context, "active_tab", "acount")

    session_company_name = request.session.get("companyName", "")

    response = get_company_by_name(session_company_name)
    company = response_data(response)

    # Por seguridad, si la respuesta no es un diccionario
    if not isinstance(company, dict):
        company = {}

    company_name = company.get("company_name", "")

    choices = get_catalogo_choices(company_name)
    values_initial = {
        "abbr": company.get("abbr", ""),
        "company_name": company.get("company_name", ""),
        "currency": company.get("default_currency", ""),
        "crear_plan_basado_en": company.get(
            "create_chart_of_accounts_based_on", ""
        ),
        "plantilla_catalogo": company.get("chart_of_accounts", ""),
        "default_cash_account": company.get("default_cash_account", ""),
        "default_bank_account": company.get("default_bank_account", ""),
        "default_expense_account": company.get(
            "default_expense_account", ""
        ),
        "default_income_account": company.get(
            "default_income_account", ""
        ),
        "default_receivable_account": company.get(
            "default_receivable_account", ""
        ),
        "default_payable_account": company.get(
            "default_payable_account", ""
        ),
        "cost_center": company.get("cost_center", ""),
        "default_inventory_account": company.get(
            "default_inventory_account", ""
        ),
        "accumulated_depreciation_account": company.get(
            "accumulated_depreciation_account", ""
        ),
        "depreciation_expense_account": company.get(
            "depreciation_expense_account", ""
        ),
        "stock_adjustment_account": company.get(
            "stock_adjustment_account", ""
        ),
        "stock_received_but_not_billed": company.get(
            "stock_received_but_not_billed", ""
        ),
        "valuation_method": company.get("valuation_method", ""),
        "default_discount_account": company.get(
            "default_discount_account", ""
        ),
        "write_off_account": company.get("write_off_account", ""),
        "unrealized_profit_loss_account": company.get(
            "unrealized_profit_loss_account", ""
        ),
        "exchange_gain_loss_account": company.get(
            "exchange_gain_loss_account", ""
        ),
        "unrealized_exchange_gain_loss_account": company.get(
            "unrealized_exchange_gain_loss_account", ""
        ),
        "payment_terms": company.get("payment_terms", ""),
        "default_finance_book": company.get("default_finance_book", ""),
    }

    form = CatalogoCuentasForm(
        request.POST or None,
        initial=values_initial,
    )

    # Muy importante: asignar choices también durante POST,
    # antes de llamar a is_valid().
    apply_form_choices(form, choices)

    form.fields["crear_plan_basado_en"].widget.attrs["readonly"] = True
    form.fields["plantilla_catalogo"].widget.attrs["readonly"] = True

    if request.method == "POST" and form.is_valid():
        datos_formulario = form.cleaned_data

        cambios = {
            campo: {
                "old": form.initial.get(campo),
                "new": valor_nuevo,
            }
            for campo, valor_nuevo in datos_formulario.items()
            if form.initial.get(campo) != valor_nuevo
        }

        logger.info("Cambios detectados: %s", cambios)

        campos_excluir = {
            "abbr",
            "company_name",
            "currency",
            "crear_plan_basado_en",
            "plantilla_catalogo",
        }

        campos_finales = [
            campo
            for campo, valor in datos_formulario.items()
            if valor and campo not in campos_excluir
        ]

        company_name = datos_formulario.get("company_name", "")

        cuentas_no_existentes, cuentas_existentes = validar_cuentas(
            campos_finales,
            datos_formulario,
        )

        cuentas_validar = cuentas_existentes + cuentas_no_existentes

        campos_guardar = comparar_valores(
            company_name,
            cuentas_validar,
        )

        resultado = guardar_cambios(
            company_name,
            campos_guardar,
        )

        if resultado:
            messages.success(request, str(resultado))

        return redirect("organization:catalogo_cuentas")

    context = agregar_atributos(context, "form", form)

    return render(
        request,
        "organization/accounts.html",
        context,
    )

@session_required("login")     
def company_cuentas(request):
    company_name = request.session.get('companyName')
    if not company_name:
        return redirect('inicio')
    return redirect(
        'organization:compania',
        name=company_name
    )
