from config.decorators import session_required
from django.shortcuts import render

@session_required("login")
def homeowner_list(request):
    return render(
        request,
        "homeowner/homeowners.html",
#        context,
    )