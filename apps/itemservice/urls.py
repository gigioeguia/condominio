from django.urls import path
from .views.itemservice import itemservice_list, itemservice_form 


app_name = "itemservice"

urlpatterns = [
    path("", itemservice_list, name="list"),
    path("new/", itemservice_form, name="new"),
    path("edit/<str:item_code>/", itemservice_form, name="edit"),
    path("delite/<str:item_code>/", itemservice_form, name="delete"),
]