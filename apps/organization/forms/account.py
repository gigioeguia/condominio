import re

from django import forms
from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
    Row,
    Column,
    HTML,
)
from django.urls import reverse

class CatalogoCuentasForm(forms.Form):
    
    SELECT_ATTRS = {"class": "form-select"}
    
    abbr = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    company_name = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    currency= forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    crear_plan_basado_en = forms.CharField(
        required=False,
    )

    plantilla_catalogo = forms.CharField(
        required=False,
    )

    # - default_cash_account
    default_cash_account = forms.ChoiceField(
        label="Cuenta de efectivo por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),
    )

    # - default_bank_account
    default_bank_account = forms.ChoiceField(
        label="Cuenta bancaria por defecto",
        required=False,
        choices=[],
        widget=forms.Select(attrs=SELECT_ATTRS),        
    )

    # - default_expense_account
    default_expense_account = forms.ChoiceField(
        label="Cuenta de costos (venta) por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS), 
    )
    
    # - default_payable_account
    default_payable_account = forms.ChoiceField(
        label="Cuenta por pagar por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),  
    )

    # - default_income_account
    default_income_account = forms.ChoiceField(
        label="Cuenta de ingresos por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS), 
    )

    # - default_receivable_account
    default_receivable_account = forms.ChoiceField(
        label="Cuenta por cobrar por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),  
    )
    
    #  - default_discount_account
    default_discount_account = forms.ChoiceField(
        label="Cuenta de descuento por pago predeterminado",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),         
    )

    payment_terms = forms.ChoiceField(
        label="Plantilla de Términos de Pago Predeterminados",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),  
    )

    write_off_account = forms.ChoiceField(
        label="Cuenta de Desajuste",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),  
    )

    # - cost_center - round_off_cost_center - depreciation_cost_center
    cost_center = forms.ChoiceField(
        label="Centro de costos por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),
    )
    # - unrealized_profit_loss_account
    unrealized_profit_loss_account = forms.ChoiceField(
        label="Cuenta de Pérdidas/Ganancias no realizada",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS), 
    )

    default_finance_book = forms.ChoiceField(
        label="Libro de Finanzas Predeterminado - ?",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS), 
    )
    # - default_inventory_account    
    default_inventory_account = forms.ChoiceField(
        label="Cuenta inventarios por defecto",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),         
    )
    # - valuation_method
    valuation_method = forms.ChoiceField(
        label="Método de Valoración de Stock predeterminado",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),           
    )
    #  - stock_adjustment_account
    stock_adjustment_account = forms.ChoiceField(
        label="Cuenta de ajuste de existencias",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),
    )
    #- accumulated_depreciation_account
    accumulated_depreciation_account = forms.ChoiceField(
        label="Cuenta de depreciación acumulada",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),        
    )
    # - depreciation_expense_account
    depreciation_expense_account = forms.ChoiceField(
        label="Cuenta de gastos de depreciación",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),          
    )
    # - stock_received_but_not_billed
    stock_received_but_not_billed= forms.ChoiceField(
        label="Inventario Recibido pero no Facturado",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),        
    )
    
    exchange_gain_loss_account= forms.ChoiceField(
        label="Cuenta de ganancias/pérdidas por enajenación de activos fijos",
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),  
    )
    
    def __init__(self, *args, **kwargs):
        choices = {
            "default_cash_account": kwargs.pop("cuentas_cash", []),
            "default_bank_account": kwargs.pop("cuentas_banco", []),
            "default_expense_account": kwargs.pop("cuentas_default_expense", []),
            "default_payable_account": kwargs.pop("cuentas_payable", []),
            "default_income_account": kwargs.pop("cuentas_default_income", []),
            "default_receivable_account": kwargs.pop("cuentas_receivable", []),
            "default_discount_account": kwargs.pop("cuentas_discount", []),
            "payment_terms": kwargs.pop("payment_terms", []),
            "write_off_account": kwargs.pop("cuentas_write_off", []),
            "cost_center": kwargs.pop("cost_center", []),
            "unrealized_profit_loss_account": kwargs.pop(
                "cuentas_unrealized_profit_loss",
                [],
            ),
            "default_finance_book": kwargs.pop("finance_book", []),
            "default_inventory_account": kwargs.pop("inventory", []),
            "valuation_method": kwargs.pop("valuation_method", []),
            "stock_adjustment_account": kwargs.pop("stock_adjustment", []),
            "accumulated_depreciation_account": kwargs.pop(
                "accumulated_depreciation",
                [],
            ),
            "depreciation_expense_account": kwargs.pop(
                "depreciation_expense",
                [],
            ),
            "stock_received_but_not_billed": kwargs.pop(
                "stock_received_but_not_billed",
                [],
            ),
            "exchange_gain_loss_account": kwargs.pop(
                "exchange_gain_loss",
                [],
            ),
        }
        
        super().__init__(*args, **kwargs)

        self._set_choices(choices)
        self._configure_crispy()
    def _set_choices(self, choices):
        for field_name, field_choices in choices.items():
            self.fields[field_name].choices = field_choices or []    
    
    
    def _configure_crispy(self):
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"

        self.helper.layout = Layout(
            Field("abbr"),
            Field("company_name"),
            Field("currency"),
            Accordion(
                AccordionGroup(
                    "Catálogo de cuentas",
                    Row(
                        Column(Field("crear_plan_basado_en"), css_class="col-md-5"),
                        Column(Field("plantilla_catalogo"), css_class="col-md-5"),
                    ),
                    active=True  # siempre abierto
                ),
                AccordionGroup(
                    "Cuentas predeterminadas",
                    Row(
                        Column(
                            Field("default_cash_account"),
                            Field("default_bank_account"),
                            Field("default_receivable_account"),
                            Field("default_payable_account"),
                            Field("write_off_account"),
                            Field("unrealized_profit_loss_account"),
                            css_class="col-md-5",
                        ),
                        Column(
                            Field("default_expense_account"),
                            Field("default_income_account"),
                            Field("default_discount_account"),
                            Field("payment_terms"),
                            Field("cost_center"),
                            Field("default_finance_book"),
                            css_class="col-md-5",
                        ),
                    ),
                    active=True  # siempre abierto
                ),
                AccordionGroup(
                    "Cuentas Almacén",
                    Row(
                        Column(Field("default_inventory_account"), Field("valuation_method"), css_class="col-md-5"),
                        Column(Field("stock_adjustment_account"), Field("stock_received_but_not_billed"), css_class="col-md-5"),
                    ),
                    active=False  # cerrado por defecto
                ),
                AccordionGroup(
                    "Cuenta de activo fijo predeterminada",
                    Row(
                        Column(Field("accumulated_depreciation_account"),Field("depreciation_expense_account"), css_class="col-md-5"),
                        Column(Field("exchange_gain_loss_account"), css_class="col-md-5"),
                    ),
                    active=False  # cerrado por defecto
                ),
            ),

            HTML(
                """
                <div class="col-12 mt-3">
                    <button type="submit" class="btn btn-primary">
                        Guardar
                    </button>
                </div>
                """
            ),
        )
