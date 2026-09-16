import django_filters

from .table import OrganizationTable


class OrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Organización",
        widget=django_filters.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar organización",
            }
        ),
    )

    abbr = django_filters.CharFilter(
        lookup_expr="icontains",
        label="Abreviatura",
        widget=django_filters.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar abreviatura",
            }
        ),
    )

    country = django_filters.CharFilter(
        lookup_expr="icontains",
        label="País",
        widget=django_filters.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Buscar país",
            }
        ),
    )

    class Meta:
        model = None
        fields = ["name", "abbr", "country"]
