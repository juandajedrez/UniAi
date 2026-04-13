from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile, SocialMedia, SocialMediaProfile, Teacher, Administrative, Student

# --- Inline para SocialMediaProfile dentro de Profile ---
class SocialMediaProfileInline(admin.TabularInline):
    model = SocialMediaProfile
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

# --- Admin para SocialMedia ---
@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ("name", "link")
    search_fields = ("name", "link")

# --- Admin para Profile ---
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "birthday", "department", "program")
    search_fields = ("user__username", "department__name", "program__name")
    list_filter = ("department", "program")
    inlines = [SocialMediaProfileInline]

# --- Admin para Teacher ---
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    search_fields = ("profile__user__username",)

# --- Admin para Administrative ---
@admin.register(Administrative)
class AdministrativeAdmin(admin.ModelAdmin):
    list_display = ("profile",)
    search_fields = ("profile__user__username",)

# --- Admin para Student ---
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("get_name", "get_program", "semester")
    search_fields = ("profile__user__username", "semester")
    list_filter = ("semester",)

    def get_name(self, obj):
        return str(obj.profile.user.first_name) + " " +str(obj.profile.user.last_name)
    get_name.short_description = "Nombre"


    def get_program(self, obj):
        return obj.profile.program
    get_program.short_description = "Programa"

