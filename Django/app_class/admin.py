from django.contrib import admin
from .models import Course, Classroom, TeacherCourse, StudentCourse, ClassroomCourse, Department, Program

# ==========================
# CONFIGURACIONES ADMIN
# ==========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("roomNumber", "capacity", "location")
    search_fields = ("roomNumber", "location")
    list_filter = ("location",)


@admin.register(TeacherCourse)
class TeacherCourseAdmin(admin.ModelAdmin):
    list_display = ("teacher", "course")
    search_fields = ("teacher__user__username", "course__name")
    list_filter = ("course",)


@admin.register(StudentCourse)
class StudentCourseAdmin(admin.ModelAdmin):
    list_display = ("student", "course")
    search_fields = ("student__user__username", "course__name")
    list_filter = ("course",)


@admin.register(ClassroomCourse)
class ClassroomCourseAdmin(admin.ModelAdmin):
    list_display = ("course", "classroom")
    search_fields = ("course__name", "classroom__roomNumber")
    list_filter = ("classroom",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "director")
    search_fields = ("name", "code", "director__username")
    ordering = ("name",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "director")
    search_fields = ("name", "code", "director__username")
    ordering = ("name",)

