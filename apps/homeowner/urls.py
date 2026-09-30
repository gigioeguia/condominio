from django.urls import path
from .views.homeowner import homeowner_list, homeowner_form_new, homeowner_form_update 

app_name = "homeowner"

urlpatterns = [
    path('', homeowner_list, name='list'),
    path("new/", homeowner_form_new, name="new"),
    path("edit/<str:customer_primary_contact>/", homeowner_form_update, name="edit"),
    path("delete/<str:customer_primary_contact>/", homeowner_form_update, name="delete"),
]