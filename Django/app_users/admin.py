from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile, SocialMedia

# --- Inline para SocialMedia dentro de Profile ---
class SocialMediaInline(admin.TabularInline):
    model = SocialMedia
    extra = 1

# --- Inline para Profile dentro de User ---
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Perfil"
    fk_name = "user"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ("username", "email", "is_staff", "is_active")
    search_fields = ("username", "email")

# Reemplazamos el admin por defecto de User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- Admin para Profile ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "department", "program", "semester", "birthday")
    search_fields = ("user__username", "user__email", "department__name", "program__name")
    list_filter = ("role", "department", "program", "semester")
    inlines = [SocialMediaInline]

# --- Admin para SocialMedia ---
@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ("name", "link", "profile")
    search_fields = ("name", "link", "profile__user__username")
    list_filter = ("name",)
