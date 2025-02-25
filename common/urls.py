from django.urls import path

from common import views

urlpatterns = [
    path("parent_list/", views.parent_list),
    path("add_child/", views.add_child),
    path("get_child/", views.get_child),
    path("change_password/", views.change_password),
    path("get_child_values/", views.get_child_values),
]
