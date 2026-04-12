from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Teacher, Administrative, Student

# --- Perfil integrado en el admin de User ---
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

# --- Modelos independientes ---
@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "officeHours")
    search_fields = ("user__username", "department")

@admin.register(Administrative)
class AdministrativeAdmin(admin.ModelAdmin):
    list_display = ("user", "department")
    search_fields = ("user__username", "department")

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "semester")
    search_fields = ("user__username", "semester")
