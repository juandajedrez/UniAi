from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("auth/", views.auth_view, name="auth"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_detail, name="profile_detail"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),
    path("socialmedia/delete/<int:pk>/", views.delete_social_media, name="delete_social_media"),
    path("contact/<int:profile_id>/", views.view_contact, name="view_contact_detail"),
    path("contacts/", views.view_contacts_list, name="view_contacts_list"),
    path("contact/<int:profile_id>/chat/", views.contact_chat, name="contact_chat"),
]
