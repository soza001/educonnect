from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("classes/", views.view_classes, name="view_classes"),
    path("emplois/", views.view_schedules, name="view_schedules"),
    path("notes/", views.view_notes, name="view_notes"),
    path("bulletins/", views.view_bulletins, name="view_bulletins"),

    # Routes protégées
    path("add-class/", views.add_class, name="add_class"),
    path("add-note/", views.add_note, name="add_note"),
    path("add-schedule/", views.add_schedule, name="add_schedule"),

    # Authentification
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("authenticate/", views.authenticate_user, name="authenticate_user"),
    path("logout/", views.logout, name="logout"),
]
