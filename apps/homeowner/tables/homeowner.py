import django_tables2 as tables


class CustomerTable(tables.Table):
    
    customer_primary_contact = tables.Column(
        visible=False
    )
    
    customer_name = tables.Column(
        verbose_name="Propiedad"
    )

    alias = tables.Column(
        verbose_name="Propitari@"
    )

    customer_type = tables.Column(
        verbose_name="Tipo de cliente"
    )

    customer_group = tables.Column(
        verbose_name="Grupo de cliente"
    )

    territory = tables.Column(
        verbose_name="Territorio"
    )
    
    actions = tables.TemplateColumn(
        template_code="""
            <div class="btn-group" role="group">
                {% if record.customer_primary_contact %}
                    <a href="{% url 'homeowner:edit' record.customer_primary_contact %}" 
                        class="btn btn-sm btn-link text-warning">
                        <i class="bi bi-pencil-square" aria-hidden="true"></i>
                    </a>
        
                    <a href="#"
                        class="btn btn-sm btn-link text-danger"
                        data-bs-toggle="modal"
                        data-bs-target="#deleteModal"
                        data-delete-url="{% url 'homeowner:delete' record.customer_name %}"
                        data-item-name="{{ record.customer_name }}">
                        <i class="bi bi-trash" aria-hidden="true"></i>
                    </a>
                {% else %}
                    <span class="text-muted" title="Contacto principal no disponible">
                        <i class="bi bi-exclamation-triangle"></i>
                    </span>
                {% endif %}    
            </div>""",
        verbose_name="Acciones",
        orderable=False
    )

    class Meta:
        template_name = "django_tables2/bootstrap5.html"
        fields = (
            "customer_primary_contact",
            "customer_name",
            "alias",
            "customer_type",
            "customer_group",
            "territory",
        )
        attrs = {
            "class": "table table-striped table-hover align-middle",
        }
