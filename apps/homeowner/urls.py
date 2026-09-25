from django.urls import path
from .views.homeowner import homeowner_list 


app_name = "homeowner"

urlpatterns = [
    path('', homeowner_list, name='list'),
]