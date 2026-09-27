import django_tables2 as tables

class ItemPriceTable(tables.Table):

    item_code = tables.Column(
        verbose_name="Código",
    )

    item_name = tables.Column(
        verbose_name="Nombre",
    )

    price_list_rate = tables.Column(
        verbose_name="Precio",
        attrs={
            "td": {
                "class": "text-end",
            }
        },
    )

    currency = tables.Column(
        verbose_name="Moneda",
    ) 

    valid_from = tables.DateColumn(
        verbose_name="Valido desde",
    )
    
    actions = tables.TemplateColumn(
        template_code="""
        <div class="btn-group" role="group">
            <a href="{% url 'itemservice:edit' record.item_code %}" 
                class="btn btn-sm btn-link text-warning">
                <i class="bi bi-pencil-square" aria-hidden="true"></i>
            </a>

            <a href="#"
                class="btn btn-sm btn-link text-danger"
                data-bs-toggle="modal"
                data-bs-target="#deleteModal"
                data-delete-url="{% url 'itemservice:delete' record.item_code %}"
                data-item-name="{{ record.item_code }}">
                <i class="bi bi-trash" aria-hidden="true"></i>
            </a>
        </div>""",
        verbose_name="Acciones",
        orderable=False
    )
    

    def render_price_list_rate(self, value, record):
        return f"${value:,.2f}"


    class Meta:
        attrs = {
            "class": "table table-striped table-hover",
        }
        empty_text = "No existen registros por mostrar"