from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

@login_required
def home_view(request):
    return render(request, "home.html")

def custom_page_not_found(request, exception):
    return render(request, "404.html", status=404)

@login_required
def blank_view(request):
    return redirect("home")

