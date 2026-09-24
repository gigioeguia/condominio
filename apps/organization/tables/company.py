from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables

class OrganizationTable(tables.Table):
    name = tables.Column(verbose_name="Organización")
    abbr = tables.Column(verbose_name="Abreviatura")
    default_currency = tables.Column(verbose_name="Moneda")
    tax_id = tables.Column(verbose_name="RFC")
    country = tables.Column(verbose_name="País")
    phone_no = tables.Column(verbose_name="Teléfono")
    email = tables.Column(verbose_name="Correo electrónico")
    website = tables.Column(verbose_name="Sitio web")
    date_of_establishment = tables.Column(
        verbose_name="Fecha de establecimiento"
    )
    
    actions = tables.TemplateColumn(
        template_name="organization/actions.html",
        verbose_name="Acciones",
        orderable=False,
        empty_values=(),
        exclude_from_export=True
    )

    class Meta:
        attrs = {
            "class": "table table-striped table-hover align-middle"
        }
        template_name = "organization/table.html"
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
            "actions"
        ]
        order_by = "name"
        
