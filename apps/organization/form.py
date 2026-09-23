import re

from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from crispy_forms.bootstrap import Accordion, AccordionGroup
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
    Row,
    Column,
    HTML,
    Submit,
    Div
)
from django.urls import reverse
import pandas as pd


class OrganizationForm(forms.Form):
    
    required_css_class = "required"
    
    action = forms.CharField(
            label="action",
            required=False,
            initial=0,
            widget=forms.HiddenInput()
    )
    
    company_name = forms.CharField(
        label="Nombre de la empresa",
        max_length=255,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\s\.\'\-&]+$',
                message="El nombre solo puede contener letras, números, espacios y los caracteres . - &",
                code="invalid_company_name"
            )
        ]
    )

    abbr = forms.CharField(
        label="Abreviatura",
        max_length=20,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-zÁÉÍÓÚÑáéíóúñ0-9\s\.\-&]+$',
                message="La abreviatura solo puede contener letras, números, espacios y los caracteres . - &",
                code="invalid_abbr"
                )
            ]
    )

    default_currency = forms.CharField(
        label="Moneda predeterminada",
        max_length=10,
        required=True,
        widget=forms.Select(
            choices=[
                ("", "Seleccione una moneda")
            ],
            attrs={
                "class": "form-select",
                "id": "id_default_currency",
                "data-placeholder": "Seleccione una moneda",
            }
        ),
    )

    tax_id = forms.CharField(
        label="RFC",
        max_length=50,
        required=False,
        validators=[
            RegexValidator(
                regex=r'^([A-ZÑ&]{3}[0-9]{6}[A-Z0-9]{3}|[A-ZÑ&]{4}[0-9]{6}[A-Z0-9]{3})$',
                message="Ingrese un RFC válido (persona física o moral).",
                code="invalid_rfc"
            )
        ]
    )
    
    country = forms.CharField(
        label="Pais",
        required=True,
        widget=forms.Select(
            choices=[
                ("", "Seleccione un país"),
            ],
            attrs={
                "class": "form-select",
                "id": "id_country",
                "data-placeholder": "Seleccione un país",
            }
        ),
    )

    domain = forms.CharField(
        label="Dominio",
        max_length=255,
        required=False,
    )

    date_of_establishment = forms.DateField(
        label="Fecha de establecimiento",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    date_of_incorporation = forms.DateField(
        label="Fecha de constitución",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    date_of_commencement = forms.DateField(
        label="Fecha de inicio de operaciones",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date"}
        ),
    )

    phone_no = forms.CharField(
        label="Teléfono",
        max_length=30,
        required=False,
    )

    fax = forms.CharField(
        label="Fax",
        max_length=30,
        required=False,
    )

    email = forms.EmailField(
        label="Correo electrónico",
        required=False,
    )

    company_description = forms.CharField(
        label="Descripción de la empresa",
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4}
        ),
    )

    website = forms.URLField(
        label="Sitio web",
        required=False,
    )

    registration_details = forms.CharField(
        label="Detalles de registro",
        required=False,
        widget=forms.Textarea(
            attrs={"rows": 4}
        ),
    )

    chart_of_accounts = forms.CharField(
        label="Plan de cuentas",
        required=False,
        widget=forms.Select(
                    attrs={
                        "class": "form-select remote-select",
                        "id": "id_chart_of_accounts",
                    }
        ),
    )

    create_chart_of_accounts_based_on = forms.CharField(
        label="Crear plan de cuentas basado en",
        required=False,
        widget=forms.Select(
                    attrs={
                        "class": "form-select remote-select",
                        "id": "id_create_chart_of_accounts_based_on",
                    }
        ),
    )
    
    """    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        tax_id = cleaned_data.get("tax_id")

        if country == "Mexico" and not tax_id:
            raise ValidationError({"tax_id": "El RFC es obligatorio cuando el país es Mexico."})

        return cleaned_data """

    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super().__init__(*args, **kwargs)
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"

        self.helper.layout = Layout(
            Field("action"),
            Row(
                Column("company_name", css_class="col-md-8"),
                Column("abbr", css_class="col-md-4"),
            ),

            Row(
                Column("default_currency", css_class="col-md-4"),
                Column("tax_id", css_class="col-md-4"),
                Column("country", css_class="col-md-4"),
            ),

            Row(
                Column("domain", css_class="col-md-6"),
                Column("email", css_class="col-md-6"),
            ),

            Row(
                Column(
                    "date_of_establishment",
                    css_class="col-md-4",
                ),
                Column(
                    "date_of_incorporation",
                    css_class="col-md-4",
                ),
                Column(
                    "date_of_commencement",
                    css_class="col-md-4",
                ),
            ),

            Row(
                Column("phone_no", css_class="col-md-4"),
                Column("fax", css_class="col-md-4"),
                Column("website", css_class="col-md-4"),
            ),
            
            "company_description",
            "registration_details",

            Row(
                Column(
                    "chart_of_accounts",
                    css_class="col-md-6",
                ),
                Column(
                    "create_chart_of_accounts_based_on",
                    css_class="col-md-6",
                ),
            ),
            Row(
                Column(
                    HTML(
                        '''
                        <button type="submit"
                                name="submit"
                                id="button-id-submit"
                                class="btn btn-primary"
                                title="Guardar"
                                aria-label="Guardar">
                            <i class="bi bi-save" aria-hidden="true"></i>
                        </button>
                        '''
                    ),
                    css_class="text-end col-md-6",
                ),    
                Column(
                    HTML(f'<a class="btn btn-secondary" href="{reverse("organization:list")}" '
                        'title="Cancelar" aria-label="Cancelar"><i class="bi bi-x-lg" aria-hidden="true"></i></a>'
                    ),
                    css_class="col-md-6"
                )
            )
        )

        #####currency
        choices = [("", "Seleccione una moneda")]
        currency = self.initial.get("default_currency")
        if currency and all(value != currency for value, label in choices):
            choices.append((currency, currency))
        self.fields["default_currency"].widget.choices = choices

        self.fields["default_currency"].widget.attrs.update({
            "data-url": reverse("organization:getCurrencies"),
        })
        
        #####country
        choices = [("", "Seleccione un Pais")]
        country = self.initial.get("country")
        if country and all(value != country for value, label in choices):
            choices.append((country, country))
        self.fields["country"].widget.choices = choices
                    
        self.fields["country"].widget.attrs.update({
            "data-url": reverse("organization:getCountries"),
        })
        
        #####chart_of_accounts
        choices = [("", "Seleccione un Plan de cuentas")]
        chart_of_accounts = self.initial.get("chart_of_accounts")
        if chart_of_accounts and all(value != chart_of_accounts for value, label in choices):
            choices.append((chart_of_accounts, chart_of_accounts))
        self.fields["chart_of_accounts"].widget.choices = choices
                    
        self.fields[ "chart_of_accounts"].widget.attrs.update({
            "data-url": reverse("organization:get_chart_templates"),
        })
        
        #####create_chart_of_accounts_based_on
        choices = [("", "Seleccione un plan de cuentas basado en")]
        create_chart_of_accounts_based_on = self.initial.get("create_chart_of_accounts_based_on")
        if create_chart_of_accounts_based_on and all(value != create_chart_of_accounts_based_on for value, label in choices):
            choices.append((create_chart_of_accounts_based_on, create_chart_of_accounts_based_on))
        self.fields["create_chart_of_accounts_based_on"].widget.choices = choices
                    
        #self.fields[ "create_chart_of_accounts_based_on"].widget.attrs.update({
        #    "data-url": reverse("organization:get_chart_templates"),
        #})
        
    def clean_action(self):
        value = self.cleaned_data.get("action")
        return 0 if value in (None, "") else value        
        
class OrganizationImportForm(forms.Form):
    archivo = forms.FileField(
        label="Seleccionar archivo",
        help_text="Formatos permitidos: CSV o XLSX."
    )
    def clean_archivo(self):
        try:
            archivo = self.cleaned_data["archivo"]

            nombre = archivo.name.lower()

            if nombre.endswith((".xlsx", ".xls")):
                df = pd.read_excel(archivo)
            elif nombre.endswith(".csv"):
                df = pd.read_csv(archivo)
            else:
                raise ValidationError(
                    "El archivo debe ser CSV o Excel."
                )

        except ValidationError:
            raise

        except Exception as e:
            raise ValidationError(
                "No se pudo leer el archivo. Verifica su formato."
            ) from e

        columnas_requeridas = {
            "company_name",
            "abbr",
            "default_currency",
            "tax_id",
            "country",
            "domain",
            "date_of_establishment",
            "date_of_incorporation",
            "date_of_commencement",
            "phone_no",
            "fax",
            "email",
            "company_description",
            "website",
            "registration_details",
            "chart_of_accounts",
            "create_chart_of_accounts_based_on",
        }

        # Conservar los encabezados originales
        columnas_originales = [
            str(columna)
            for columna in df.columns
        ]

        # Buscar espacios al principio, al final o dentro del encabezado
        columnas_con_espacios = [
            columna
            for columna in columnas_originales
            if re.search(r"\s", columna)
        ]

        if columnas_con_espacios:
            raise ValidationError(
                "Los encabezados no deben contener espacios al inicio, "
                "al final ni entre palabras: "
                + ", ".join(
                    repr(columna)
                    for columna in columnas_con_espacios
                )
            )

        # Validar que los encabezados estén en minúsculas
        columnas_mayusculas = [
            columna
            for columna in columnas_originales
            if columna != columna.lower()
        ]

        if columnas_mayusculas:
            raise ValidationError(
                "Los encabezados deben estar escritos en minúsculas: "
                + ", ".join(columnas_mayusculas)
            )

        # No se usa strip(), porque los espacios ya fueron rechazados
        df.columns = [
            columna.lower()
            for columna in columnas_originales
        ]

        # Verificar encabezados duplicados
        columnas_duplicadas = [
            columna
            for columna in set(df.columns)
            if list(df.columns).count(columna) > 1
        ]

        if columnas_duplicadas:
            raise ValidationError(
                "Existen encabezados duplicados: "
                + ", ".join(sorted(columnas_duplicadas))
            )

        columnas_archivo = set(df.columns)

        faltantes = columnas_requeridas - columnas_archivo

        if faltantes:
            raise ValidationError(
                "Faltan las siguientes columnas: "
                + ", ".join(sorted(faltantes))
            )

        columnas_adicionales = columnas_archivo - columnas_requeridas

        if columnas_adicionales:
            raise ValidationError(
                "El archivo contiene columnas no permitidas: "
                + ", ".join(sorted(columnas_adicionales))
            )

        if len(df) != 1:
            raise ValidationError(
                "El archivo debe contener exactamente 1 registro. "
                f"Se encontraron {len(df)}."
            )

        primer_registro = df.iloc[0]
        campos_vacios = []

        for campo in columnas_requeridas:
            valor = primer_registro[campo]

            if pd.isna(valor) or not str(valor).strip():
                campos_vacios.append(campo)

        if campos_vacios:
            raise ValidationError(
                "El primer registro tiene vacíos los campos: "
                + ", ".join(sorted(campos_vacios))
            )

        # Reiniciar el cursor para una lectura posterior
        archivo.seek(0)

        return archivo

class ImportJsonForm(forms.Form):
    date_of_establishment = "2026-08-01" 
    initial = (
        "{\n"
        "    \"company_name\": \"company-json\",\n"
        "    \"abbr\": \"JSON\",\n"
        "    \"default_currency\": \"MXN\",\n"
        "    \"tax_id\": \"RFC123456789\",\n"
        "    \"country\": \"Mexico\",\n"
        "    \"domain\": \"laloscondominio.com.mx\",\n"
        "    \"date_of_establishment\": \"" + date_of_establishment + "\",\n"
        "    \"date_of_incorporation\": \"" + date_of_establishment + "\",\n"
        "    \"date_of_commencement\": \"" + date_of_establishment + "\",\n"
        "    \"phone_no\": \"525512345678\",\n"
        "    \"fax\": \"525512345678\",\n"
        "    \"email\": \"info@laloscondominioscom.mx\",\n"
        "    \"company_description\": \"Administración de condominios y bienes raíces en Mexico.\",\n"
        "    \"website\": \"https://laloscondominio.com.mx\",\n"
        "    \"registration_details\": \"Inscrita en el Registro Público de Comercio, Folio 987654\",\n"
        "    \"chart_of_accounts\": \"Mexico - Plan de Cuentas\",\n"
        "    \"create_chart_of_accounts_based_on\": \"Standard Template\"\n"
        "}"
    )
    
    text = forms.CharField(
        label="JSON",
        required=True,
        initial= initial,
        widget=forms.Textarea(attrs={
            "rows": 15,
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_action = ""

        self.helper.layout = Layout(
            "text",
            Row(
                Column(
                    HTML(
                        '''
                        <button type="submit"
                                name="submit"
                                id="button-id-submit"
                                class="btn btn-primary"
                                title="Guardar"
                                aria-label="Guardar">
                            <i class="bi bi-save" aria-hidden="true"></i>
                        </button>
                        '''
                    ),
                    css_class="text-end col-md-6",
                ), 
                Column(
                    HTML(
                        f'<a class="btn btn-secondary" href="{reverse("organization:list")}" '
                            'title="Cancelar" aria-label="Cancelar"><i class="bi bi-x-lg" aria-hidden="true"></i></a>'
                    ),
                    css_class="col-md-6"
                ),
                css_class="mt-3"
            ),
        )

class OrganizationFilterForm(forms.Form):
    name = forms.CharField(
        required=False,
        label="Nombre",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Buscar por nombre",
                "class": "form-control",
            }
        ),
    )

    abbr = forms.CharField(
        required=False,
        label="Abreviatura",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Abreviatura",
                "class": "form-control",
            }
        ),
    )

    country = forms.CharField(
        required=False,
        label="País",
        widget=forms.TextInput(
            attrs={
                "placeholder": "País",
                "class": "form-control",
            }
        ),
    )
    
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
        
class EmailAccountForm(forms.Form):
    email_id = forms.EmailField(
        label="Dirección de correo electrónico",
        required=True,
    )

    service = forms.ChoiceField(
        label="Servicios",
        choices=[
            ("", "Seleccione un servicio"),
            ("IMAP", "IMAP"),
            ("POP", "POP"),
            ("Exchange", "Exchange"),
            ("Gmail", "Gmail"),
            ("Outlook", "Outlook"),
        ],
        required=False,
    )

    company = forms.CharField(
        label="Compañía",
        required=True,
    )

    domain = forms.CharField(
        label="Dominio",
        required=False,
    )

    email_account_name = forms.CharField(
        label="Nombre de Cuenta de Correo Electrónico",
        required=True,
        help_text='ej. "Soporte", "Ventas", "Jerry Yang"',

    )

    enable_incoming = forms.BooleanField(
        label="Habilitar correos entrantes",
        required=False,
    )

    enable_outgoing = forms.BooleanField(
        label="Habilitar correos salientes",
        required=False,
    )

    authentication_method = forms.ChoiceField(
        label="Método",
        choices=[
            ("Basic", "Básico"),
            ("OAuth", "OAuth"),
        ],
        initial="Basic",
        required=True,
    )

    email_login = forms.EmailField(
        label="Utilice un correo electrónico diferente",
        required=False,
    )

    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(
            render_value=False,
            attrs={
                "autocomplete": "new-password",
            },
        ),
    )

    awaiting_password = forms.BooleanField(
        label="Esperando Contraseña",
        required=False,
    )

    use_ascii_for_password = forms.BooleanField(
        label="Use la codificación ASCII para la contraseña",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"
        self.helper.label_class = "form-label"

        self.helper.layout = Layout(
            HTML("<h5 class='mb-4'>Cuenta Correo</h5>"),
            Row(
                Column("email_id", css_class="col-md-6"),
                Column("service", css_class="col-md-6"),
            ),

            Row(
                Column("company", css_class="col-md-6"),
                Column("domain", css_class="col-md-6"),
            ),

            Row(
                Column("email_account_name", css_class="col-md-6"),
            ),

            Row(
                Column("enable_incoming", css_class="col-md-6"),
                Column("enable_outgoing", css_class="col-md-6"),
            ),

            HTML("<hr><h5 class='mb-4'>Autenticación</h5>"),

            Row(
                Column("authentication_method", css_class="col-md-6"),
                Column("email_login", css_class="col-md-6"),
            ),

            Row(
                Column("password", css_class="col-md-6"),
            ),

            Row(
                Column("awaiting_password", css_class="col-md-6"),
                Column("use_ascii_for_password", css_class="col-md-6"),
            ),

            HTML("<hr>"),

            Div(
                Submit(
                    "submit",
                    "Guardar cuenta",
                    css_class="btn btn-primary",
                ),
                HTML(
                    '<a href="{% url "organization:company_email" %}" '
                    'class="btn btn-secondary ms-2">Cancelar</a>'
                ),
                css_class="mt-3",
            ),
        ) 
                