from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables
        
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