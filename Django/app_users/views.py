from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm
from django.contrib.auth import logout

def auth_view(request):
    login_form = LoginForm()
    register_form = RegisterForm()

    if request.method == "POST":
        if "login_submit" in request.POST:  # botón de login
            login_form = LoginForm(request.POST)
            if login_form.is_valid():
                cd = login_form.cleaned_data
                user = authenticate(
                    request,
                    username=cd['username'],
                    password=cd['password']
                )
                if user is not None:
                    if user.is_active:
                        login(request, user)
                        return redirect('home')
                    else:
                        return HttpResponse("Disabled account")
                else:
                    return HttpResponse("Invalid login")

        elif "register_submit" in request.POST:  # botón de registro
            register_form = RegisterForm(request.POST)
            if register_form.is_valid():
                user = register_form.save(commit=False)
                user.set_password(register_form.cleaned_data["password"])
                user.save()
                login(request, user)  # inicia sesión automáticamente
                return redirect("home")

    return render(request, "login.html", {
        "login_form": login_form,
        "register_form": register_form
    })



def logout_view(request):
    logout(request)  # cierra la sesión
    return redirect("auth")  # redirige al login
