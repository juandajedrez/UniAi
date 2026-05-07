from Django.utils.logger import log_dic, log_error, log_info, log_success, log_debug
log_debug("Cargando vistas de Users")

from django.shortcuts import render, redirect, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, UserForm, ProfileForm, SocialMediaForm
from django.contrib.auth import logout
from .models import Profile, SocialMedia
from django.contrib.auth.decorators import login_required
from app_chat.models import Chat
from django.contrib import messages
from .signals import user_registered, user_registered_error
from Django.utils.scripts import generate_reset_code, send_reset_code

def auth_view(request):
    login_form = LoginForm()
    if request.method == "POST":
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            log_debug(f"Formulario válido: {login_form.cleaned_data}")  # Debug: Verificar datos limpios del formulario
            cd = login_form.cleaned_data
            user = authenticate(
                request,
                username=cd['username'],
                password=cd['password']
            )
            if user is not None:
                if user.is_active:
                    login(request, user)
                    if user.is_superuser:
                        # Redirige al panel de administración
                        return redirect('/admin/panel/')
                    else:
                        return redirect('home')
                else:
                    return HttpResponse("Disabled account")
            else:
                return HttpResponse("Invalid login")

    return render(request, "login.html", {
        "login_form": login_form,
    })

@login_required
def register_view(request):
    error_message = None  # variable para mensajes de error

    if request.method == "POST":
        if request.user.is_superuser:
            form = RegisterForm(request.POST)
            if form.is_valid():
                log_dic("Formulario válido: ", form.cleaned_data)  # Debug: Verificar datos limpios del formulario
                # Construir diccionario user_params desde los campos del form
                user_params = {
                    "username": form.cleaned_data["username"],
                    "first_name": form.cleaned_data["first_name"],
                    "last_name": form.cleaned_data["last_name"],
                    "email": form.cleaned_data["email"],
                }

                # Construir diccionario profile_params desde los campos del form
                profile_params = {
                    "role": form.cleaned_data["role"],
                    "birthday": form.cleaned_data["birthday"],
                    "department": form.cleaned_data["department"],
                    "program": form.cleaned_data["program"],
                }
                #Creamos los parametros por defecto para el usuario
                password = user_params["username"] # Contraseña por defecto (puede ser cambiada por el usuario)
                user= None
                profile = None
                # Creamos el usuario y las instancias relacionadas
                try:
                    log_info(f"Creando usuario con username: {user_params['username']} y email: {user_params['email']}") 
                    log_dic("Parámetros del usuario: ", user_params)
                    log_dic("Parámetros del perfil: ", profile_params)
                    user = User.objects.create(**user_params, password=password)
                    semester = 1 if profile_params["role"] == "STUDENT" else None
                    profile = Profile.objects.create(user=user, **profile_params, semester=semester)
                    user_registered.send(sender=Profile, profile=profile)  # Enviar señal de usuario registrado  
                except Exception as e:
                    log_error(f"Error al crear usuario", {e})
                    messages.error(request, "Error al crear el usuario.")
                    user_registered_error.send(sender=Profile, profile=profile)  
                    return render(request, "register.html", {"form": form, "error_message": error_message})

                log_success(f"Usuario configurado: {user.username}")  # Debug: Verificar creación del usuario
                return redirect("home")
            else:
                error_message = "El formulario contiene errores. Revisa los campos."
        else:
            error_message = "Solo los superusuarios pueden registrar nuevos usuarios."
            form = RegisterForm(request.POST)  # para mostrar datos ingresados
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form, "error_message": error_message})


# Caso 1: Usuario no logueado, pide reset por correo
def password_reset_request_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        try:
            user = User.objects.get(username=username)
            code = generate_reset_code()
            request.session["reset_user_id"] = user.id
            request.session["reset_code"] = code
            send_reset_code(user.email, code)
            messages.success(request, "Se envió un código de verificación a tu correo.")
            return redirect("password_reset_confirm")
        except User.DoesNotExist:
            messages.error(request, "No existe un usuario con ese nombre de usuario.")
    return render(request, "password_reset_request.html")

def password_reset_confirm_view(request):
    if request.method == "POST":
        code = request.POST.get("code")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
        elif code != request.session.get("reset_code"):
            messages.error(request, "El código es incorrecto.")
        else:
            user_id = request.session.get("reset_user_id")
            user = User.objects.get(id=user_id)
            user.set_password(new_password)
            user.save()
            messages.success(request, "Tu contraseña ha sido restablecida.")
            return redirect("auth")

    return render(request, "password_reset_confirm.html")

@login_required
def password_change_view(request):
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password != confirm_password:
            messages.error(request, "Las contraseñas no coinciden.")
        elif not request.user.check_password(old_password):
            messages.error(request, "La contraseña actual es incorrecta.")
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, "Tu contraseña ha sido cambiada correctamente.")
            return redirect("home")

    return render(request, "password_change.html")


@login_required
def password_reset_done_view(request):
    return render(request, "password_reset_done.html")



def logout_view(request):
    logout(request)  # cierra la sesión
    return redirect("auth")  # redirige al login



@login_required
def profile_detail(request):
    profile = get_object_or_404(Profile, user=request.user)
    social_media_list = SocialMedia.objects.filter(profile=profile)
    return render(request, "profile_detail.html", {
        "profile": profile,
        "social_media_list": social_media_list
    })

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    user = request.user
    social_media_qs = SocialMedia.objects.filter(profile=profile)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        social_media_form = SocialMediaForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            if user_form.cleaned_data.get("password"):
                user.set_password(user_form.cleaned_data["password"])
            user.save()

            profile_form.save()

            if social_media_form.is_valid() and social_media_form.cleaned_data.get("name"):
                sm = social_media_form.save(commit=False)
                sm.profile = profile
                sm.save()

            return redirect("profile_detail")
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
        social_media_form = SocialMediaForm()

    return render(request, "edit_profile.html", {
        "user_form": user_form,
        "profile_form": profile_form,
        "social_media_form": social_media_form,
        "social_media_list": social_media_qs
    })

@login_required
def delete_social_media(request, pk):
    profile = get_object_or_404(Profile, user=request.user)
    social_media = get_object_or_404(SocialMedia, pk=pk, profile=profile)
    social_media.delete()
    return redirect("edit_profile")

@login_required
def view_contact(request, profile_id):
    # Obtener el perfil
    profile = get_object_or_404(Profile, pk=profile_id)

    # Obtener las redes sociales asociadas
    social_media_list = SocialMedia.objects.filter(profile=profile)

    return render(request, "contact_detail.html", {
        "profile": profile,
        "social_media_list": social_media_list,
    })


@login_required
def view_contacts_list(request):
    query = request.GET.get("q", "")

    profiles = Profile.objects.select_related("user", "department", "program")

    if query:
        profiles = profiles.filter(
            user__first_name__icontains=query
        ) | profiles.filter(
            user__last_name__icontains=query
        )

    return render(request, "contacts_list.html", {"profiles": profiles})

@login_required
def contact_chat(request, profile_id):
    other_profile = get_object_or_404(Profile, pk=profile_id)
    other_user = other_profile.user

    # Buscar si ya existe un chat entre el usuario actual y el otro
    chat = Chat.objects.filter(users=request.user).filter(users=other_user).first()

    if not chat:
        # Crear nuevo chat 1 a 1
        chat = Chat.objects.create(
            description=f"Chat entre {request.user.first_name} y {other_user.first_name}",
            state="active",  # ajusta según tu modelo
            icon="https://cdn-icons-png.flaticon.com/512/1384/1384055.png"  # ícono por defecto
        )
        chat.users.add(request.user, other_user)

    # Redirigir al chat
    return redirect("chat_view", chat_id=chat.id)
