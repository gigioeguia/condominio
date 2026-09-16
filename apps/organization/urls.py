from django.urls import path

from . import views

app_name = "organization"

urlpatterns = [
  path('', views.companias_list, name='list'),
  path("compania/", views.compania, name="compania_create"),
  path('compania/<str:name>/', views.compania, name='compania'),
  
  path('delete/<str:name>/', views.delete, name='delete'), 
  
  path('getCurrencies/', views.get_currencies, name="getCurrencies" ),
  path('getCountries/', views.get_countries, name="getCountries" ),
  path('get_chart_templates/', views.get_chart_templates, name="get_chart_templates" ),
  path('get_detalle/<str:name>/', views.get_detalle, name="get_detalle" ),
  
  path('import_file/', views.organization_import_file, name="import_file" ),
  path('import_json/', views.organization_import_json, name="import_json" ),
  
  path( "catalogo_cuentas/", views.catalogo_cuentas, name="catalogo_cuentas" ),
]