from django.urls import path
from .views.itemservice import itemservice_list, itemservice_form, itemservice_form_new 


app_name = "itemservice"

urlpatterns = [
    path("", itemservice_list, name="list"),
    path("new/", itemservice_form_new, name="new"),
    path("edit/<str:item_code>/", itemservice_form, name="edit"),
    path("delite/<str:item_code>/", itemservice_list, name="delete"),
]