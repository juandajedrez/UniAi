from django.shortcuts import render, redirect, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .forms import LoginForm, RegisterForm, UserForm, ProfileForm, SocialMediaForm
from django.contrib.auth import logout
from .models import Profile, SocialMedia
from django.contrib.auth.decorators import login_required
from app_chat.models import Chat


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
                        if user.is_superuser:
                            # Redirige al panel de administración
                            return redirect('/admin/panel/')
                        else:
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
