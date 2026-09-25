from django.urls import path
from .views.subscription import subscription_list 


app_name = "subscription"

urlpatterns = [
    path('', subscription_list, name='list'),
]