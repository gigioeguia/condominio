from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Layout,
    Row,
    Column,
    HTML,
    Div
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
            ("Frappe Mail","Frappe Mail"),
            ("Sendgrid","Sendgrid"),
            ("SparkPost","SparkPost"),
            ("Exchange", "Exchange"),
            ("GMail", "GMail"),
            ("Outlook", "Outlook"),
        ],
        required=True,
    )

    company = forms.CharField(
        label="Compañía",
        required=True,
        disabled=True,
    )
    #TO_DO: falta una vista para agregar el Dominio    
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

    password = forms.CharField(
        label="Contraseña",
        required=False,
        widget=forms.PasswordInput(
            render_value=True,
            attrs={
                "autocomplete": "new-password",
            },
        ),
        help_text='Por seguridad no se muestra la contraseña, solo puedes modifiar por una nueva',
    )

    awaiting_password = forms.BooleanField(
        label="Esperando Contraseña",
        required=False,
    )

    use_ascii_for_password = forms.BooleanField(
        label="Use la codificación ASCII para la contraseña",
        required=False,
    )

    def __init__(self, *args, company=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["company"].initial = company
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
                HTML(
                    '<button type="submit" name="submit" '
                    'class="btn btn-primary">'
                    '<i class="bi bi-save me-1" aria-hidden="true"></i>'
                    '</button>'
                ),
                HTML(
                    '<a href="{% url "organization:company_email" %}" '
                    'class="btn btn-secondary ms-2"><i class="bi bi-x-lg" aria-hidden="true"></i></a>'
                ),
                css_class="d-flex justify-content-end mt-3",
            ),
        ) 
               