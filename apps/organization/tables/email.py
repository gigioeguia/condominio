from django.urls import reverse
from django.utils.html import format_html
import django_tables2 as tables
        
class ActionsColumn(tables.Column):
    empty_values = ()

    def render(self, value, record):
        name = record.get("name")

        edit_url = reverse(
            "organization:email_create_update",
            kwargs={"name": name},
        )
        delete_url = reverse(
            "organization:email_account_delete",
            kwargs={"name": name},
        )

        return format_html(
            """
            <div class="btn-group btn-group-sm" role="group">
                <a href="{}" class="btn btn-link">
                    <i class="bi bi-pencil-square" aria-hidden="true"></i>
                </a>
                <a href="{}" class="btn btn-link">
                    <i class="bi bi-trash" aria-hidden="true"></i>
                </a>
            </div>
            """,
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