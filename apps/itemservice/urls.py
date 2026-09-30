from django.urls import path
from .views.itemservice import itemservice_list, itemservice_form, itemservice_form_new, itemservice_delete 


app_name = "itemservice"

urlpatterns = [
    path("", itemservice_list, name="list"),
    path("new/", itemservice_form_new, name="new"),
    path("edit/<str:item_code>/", itemservice_form, name="edit"),
    path("delete/<str:item_code>/", itemservice_delete, name="delete"),
]