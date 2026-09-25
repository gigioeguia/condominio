from config.decorators import session_required
from django.shortcuts import render

@session_required("login")
def subscription_list(request):
    return render(
        request,
        "subscription/subscription.html",
#        context,
    )