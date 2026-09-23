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
        
class ActionsColumn(tables.Column):
    empty_values = ()

    def render(self, value, record):
        name = record.get("name")

        detail_url = reverse(
            "organization:email_account_detail",
            kwargs={"name": name},
        )
        edit_url = reverse(
            "organization:email_account_edit",
            kwargs={"name": name},
        )
        delete_url = reverse(
            "organization:email_account_delete",
            kwargs={"name": name},
        )

        return format_html(
            """
            <div class="btn-group btn-group-sm" role="group">
                <a href="{}" class="btn btn-info">
                    Detalle
                </a>
                <a href="{}" class="btn btn-warning">
                    Editar
                </a>
                <a href="{}" class="btn btn-danger">
                    Eliminar
                </a>
            </div>
            """,
            detail_url,
            edit_url,
            delete_url,
        )


class EmailAccountTable(tables.Table):
    name = tables.Column(
        verbose_name="Nombre",
    )

    email_id = tables.Column(
        verbose_name="Correo",
    )

    company = tables.Column(
        verbose_name="Empresa",
    )

    enable_incoming = tables.BooleanColumn(
        verbose_name="Entrada",
        yesno=("Sí", "No"),
    )

    enable_outgoing = tables.BooleanColumn(
        verbose_name="Salida",
        yesno=("Sí", "No"),
    )

    actions = ActionsColumn(
        verbose_name="Acciones",
        orderable=False,
    )

    class Meta:
        template_name = "django_tables2/bootstrap5.html"
        attrs = {
            "class": "table table-striped table-hover align-middle",
        }
        order_by = "name"