from django.urls import path
from execution import views

urlpatterns = [
    path('owner_registration/', views.owner_registration),
    path('get_role/', views.get_role_type),
    path('get_res/', views.get_res_type),
    path('owner_list/', views.owner_list),
    path('view_owners/', views.view_owners),
    path('parent_list/', views.parent_list),
    path('add_child/', views.add_child),
    path('get_child/', views.get_child)
]
