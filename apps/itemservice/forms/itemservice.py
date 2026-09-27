from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, HTML, Row, Column, Submit, Field

ITEM_GROUPS = [
    ("Servicios", "Servicios"),
]

UOM_CHOICES = [
    ("Nos", "Nos"),
]


class ItemServiceForm(forms.Form):
    item_code = forms.CharField(
        label="Código",
        max_length=50,
        required=True
    )

    item_name = forms.CharField(
        label="Nombre",
        max_length=140,
        required=True
    )

    description = forms.CharField(
        label="Descripción",
        widget=forms.Textarea(attrs={"rows": 3}),
        required=False
    )

    item_group_name = forms.ChoiceField(
        label="Grupo",
        choices=ITEM_GROUPS
    )

    stock_uom = forms.ChoiceField(
        label="Unidad de Medida",
        choices=UOM_CHOICES,
        required=False,
        initial="Nos"
    )

    is_sales_item = forms.BooleanField(
        label="Venta",
        required=False,
        initial=True
    )

    is_purchase_item = forms.BooleanField(
        label="Compra",
        required=False
    )

    price_list_rate = forms.DecimalField(
        label="Precio",
        max_digits=12,
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(
        attrs={
            "class": "form-control",
            "step": "1.00",
            "placeholder": "$ 0.00"
            }
        )
    )
    
    currency = forms.CharField(
        label="Moneda",
        max_length=3,
        initial="MXN",
        required=False
    )
    
    name_price = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Field("name_price"),
            Row(
                Column("item_code", css_class="col-md-4"),
                Column("item_name", css_class="col-md-8"),
            ),
            Row(
                Column("description", css_class="col-md-12"),
            ),
            Row(
                Column("item_group_name", css_class="col-md-6"),
                Column("stock_uom", css_class="col-md-6"),
            ),
            Row(
                Column("price_list_rate", css_class="col-md-3"),
                Column("currency", css_class="col-md-3"),
            ),
            HTML("""
                <hr>
                <h5 class="mt-3 mb-3">Atributos servicio</h5>
            """),
            Row(
                Column("is_sales_item", css_class="col-md-3"),
                Column("is_purchase_item", css_class="col-md-3"),
            ),
            Submit("submit", "Guardar", css_class="btn btn-primary")
        )