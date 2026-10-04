from django import forms
from django.contrib.sites import requests
from django.utils.html import escape
from crispy_forms.helper import FormHelper, reverse
from crispy_forms.layout import Layout, HTML, Row, Column, Field
from ..services.addres import get_type_address_choices

class AddressForm(forms.Form):
    name= forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    email_id = forms.EmailField(
        required=False,
        widget=forms.HiddenInput()
    )

    phone = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    fax = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    tax_category = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    disabled = forms.BooleanField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    address_title = forms.CharField(
        label="Propiedad",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
                "readonly": "readonly",
            }
        ),
    )
    
    address_type = forms.ChoiceField(
        label="Tipo de dirección",
        required=True,
        choices=get_type_address_choices(),
        initial="Facturación",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    address_line1 = forms.CharField(
        label="Dirección línea 1",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    address_line2 = forms.CharField(
        label="Dirección línea 2",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    city = forms.CharField(
        label="Ciudad",
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    is_primary_address = forms.BooleanField(
        label="Dirección de facturación preferida",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    county = forms.CharField(
        label="Municipio",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    is_shipping_address = forms.BooleanField(
        label="Dirección de envío preferida",
        required=False,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input",
            }
        ),
    )

    state = forms.CharField(
        label="Estado",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
            }
        ),
    )

    country = forms.ChoiceField(
        label="País",
        required=True,
        choices=[
            ("México", "México"),
            ("Estados Unidos", "Estados Unidos"),
            ("Canadá", "Canadá"),
        ],
        initial="México",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    pincode = forms.CharField(
        label="Código postal",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "maxlength": "10",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.form_class = "row g-3"

        self.helper.layout = Layout(
            Field("name"),
            Field("email_id"),
            Field("phone"),
            Field("tax_category"),
            Field("disabled"),
            Row(
                Column(
                    Field("address_title"),
                    Field("address_line1"),
                    Field("city"),
                    Field("state"),
                    Field("pincode"),
                    css_class="col-md-6",
                ),

                Column(
                    Field("address_type"),
                    Field("address_line2"),
                    Field("county"),
                    Field("country"),
                    Field(
                        "is_primary_address",
                        wrapper_class="form-check mb-3",
                    ),
                    Field(
                        "is_shipping_address",
                        wrapper_class="form-check mb-3",
                    ),

                    css_class="col-md-6",
                ),
                css_class="g-4",
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
                    HTML(f'<a class="btn btn-secondary" href="{reverse("homeowner:list")}" '
                          'title="Cancelar" aria-label="Cancelar"><i class="bi bi-x-lg" aria-hidden="true"></i></a>'
                        ),
                    css_class="col-md-6"
                )
            )   
        )
    