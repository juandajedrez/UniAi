from django.contrib import admin
from .models import Classroom, Course, Department, Program

# --- Admin para Classroom ---
@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("roomNumber", "location", "capacity")
    search_fields = ("roomNumber", "location")
    list_filter = ("location",)

# --- Admin para Course ---
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "get_classrooms", "get_teachers", "get_students")
    search_fields = ("name", "description", "teachers__user__username", "students__user__username")
    list_filter = ("classrooms", "teachers__role", "students__role")

    def get_classrooms(self, obj):
        return ", ".join([c.roomNumber for c in obj.classrooms.all()])
    get_classrooms.short_description = "Aulas"

    def get_teachers(self, obj):
        return ", ".join([t.user.username for t in obj.teachers.all()])
    get_teachers.short_description = "Docentes"

    def get_students(self, obj):
        return ", ".join([s.user.username for s in obj.students.all()])
    get_students.short_description = "Estudiantes"

# --- Admin para Department ---
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "director")
    search_fields = ("name", "code", "director__username")
    list_filter = ("code",)

# --- Admin para Program ---
@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "director")
    search_fields = ("name", "code", "director__username")
    list_filter = ("code",)
