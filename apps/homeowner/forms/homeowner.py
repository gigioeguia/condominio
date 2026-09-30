from django import forms
from crispy_forms.helper import FormHelper, reverse
from crispy_forms.layout import Layout, HTML, Row, Column, Field
from ..services.homeowner import choicesCustomerType, choicesCustomerGroup, choicesTerritory

class CondominoForm(forms.Form):
    
    customer_primary_contact = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    name = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    customer_name = forms.CharField(
        label="Propiedad",
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Casa 01, Departamento 01, Villa 01'})
    )
    
    alias = forms.CharField(
        label="Propietario",
        max_length=70,
        widget=forms.TextInput(attrs={'placeholder': 'Ej. Juan Pérez'})
    )
    
    mobile_no = forms.CharField(
        label="Teléfono móvil",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Ej. +52 555 123 4567",
                "type": "tel",
                "class": "form-control",
            }
        ),
    )

    email_id = forms.EmailField(
        label="Correo electrónico",
        max_length=140,
        required=False,
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Ej. juan@correo.com",
                "class": "form-control",
            }
        ),
    )

    customer_type = forms.ChoiceField(
        label="Tipo de Cliente",
        choices=choicesCustomerType,
        initial='Individual'
    )
    customer_group = forms.ChoiceField(
        label="Grupo de Cliente",
        choices=choicesCustomerGroup,
        initial='All Customer Groups'
    )
    territory = forms.ChoiceField(
        label="Territorio",
        choices=choicesTerritory,
        initial='All Territories'
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field("name"),
            Field("customer_primary_contact"),
            Row(
                Column('customer_name', css_class='form-group col-md-6 mb-3'),
                Column('alias', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column(
                    "mobile_no",
                    css_class="form-group col-md-6 mb-3",
                ),
                Column(
                    "email_id",
                    css_class="form-group col-md-6 mb-3",
                ),
            ),
            Row(
                Column('customer_type', css_class='form-group col-md-6 mb-3'),
                Column('customer_group', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('territory', css_class='form-group col-md-6 mb-3'),
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