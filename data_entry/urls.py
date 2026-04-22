from django.urls import path

from . import views

app_name = "data_entry"

urlpatterns = [
    path("", views.spa, name="home"),
    path("about/", views.spa, name="about"),
    path("login/", views.spa, name="login"),
    path("register/", views.spa, name="register"),
    path("projects/", views.spa, name="projects"),
    path("project/<int:project_id>/", views.spa, name="project_detail"),
    path(
        "project/<int:project_id>/work/<int:work_id>/",
        views.spa,
        name="work_detail",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/monitoring/",
        views.spa,
        name="work_monitoring",
    ),
    path("logout/", views.logout_view, name="logout"),
    path(
        "project/<int:project_id>/delete/",
        views.delete_project,
        name="delete_project",
    ),
    path(
        "project/<int:project_id>/close/",
        views.close_project,
        name="close_project",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/delete/",
        views.delete_work,
        name="delete_work",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/activity/<int:activity_id>/delete/",
        views.delete_activity,
        name="delete_activity",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/activity/<int:activity_id>/toggle/",
        views.toggle_activity,
        name="toggle_activity",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/activity/<int:activity_id>/evaluate/",
        views.update_evaluation,
        name="update_evaluation",
    ),
    path(
        "project/<int:project_id>/work/<int:work_id>/activity/<int:activity_id>/upload/",
        views.upload_activity_photos,
        name="upload_activity_photos",
    ),
]
