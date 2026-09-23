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
  path( "company_cuentas/", views.company_cuentas, name="company_cuentas" ),
  path( "company_email/", views.company_email, name="company_email" ),
  
  path( "imprimir/<str:name>/", views.imprimir, name="imprimir" ),
  
  path( "email_account/<str:name>/", views.company_email, name="email_account_detail"),
  path( "email_account/<str:name>/edit//", views.company_email, name="email_account_edit"),
  path( "email_account<str:name>/delete/", views.company_email, name="email_account_delete"), 
  
  path( "email_create_update/", views.email_create_update, name="email_create_update" ),
  path( "save_email_account", views.save_email_account, name="save_email_account"),
  
]