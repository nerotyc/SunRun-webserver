from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse


# Create your views here.
def root_view(request, *args, **kargs):
    return redirect("/dashboard/")
    # return render(request, "dashboard.html", {})


def contact_view(request, *args, **kargs):
    return redirect("https://djk-sonnen.de/kontakt/")


def imprint_view(request, *args, **kargs):
    return redirect("https://djk-sonnen.de/impressum/")
