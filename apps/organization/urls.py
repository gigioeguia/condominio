from django.urls import path

from .views.company import companias_list, compania, delete, get_currencies, get_countries, get_chart_templates, get_detalle, \
                           organization_import_file, organization_import_json, imprimir
from .views.account import catalogo_cuentas, company_cuentas
from .views.email import company_email, email_create_update, save_email_account

app_name = "organization"

urlpatterns = [
  path('', companias_list, name='list'),
  path("compania/", compania, name="compania_create"),
  path('compania/<str:name>/', compania, name='compania'),
  
  path('delete/<str:name>/', delete, name='delete'), 
  
  path('getCurrencies/', get_currencies, name="getCurrencies" ),
  path('getCountries/', get_countries, name="getCountries" ),
  path('get_chart_templates/', get_chart_templates, name="get_chart_templates" ),
  path('get_detalle/<str:name>/', get_detalle, name="get_detalle" ),
  
  path('import_file/', organization_import_file, name="import_file" ),
  path('import_json/', organization_import_json, name="import_json" ),
  
  path( "catalogo_cuentas/", catalogo_cuentas, name="catalogo_cuentas" ),
  path( "company_cuentas/", company_cuentas, name="company_cuentas" ),
  
  path( "company_email/", company_email, name="company_email" ),
  
  path( "imprimir/<str:name>/", imprimir, name="imprimir" ),
  
  path( "email_account/<str:name>/", company_email, name="email_account_detail"),
  path( "email_account/<str:name>/edit//", company_email, name="email_account_edit"),
  path( "email_account<str:name>/delete/", company_email, name="email_account_delete"), 
  
  path( "email_create_update/", email_create_update, name="email_create_update" ),
  path( "save_email_account", save_email_account, name="save_email_account"),
  
]