from django.urls import path
from execution import views

urlpatterns = [
    path('owner_registration/', views.owner_registration),
    path('get_role/', views.get_role_type),
    path('get_res/', views.get_res_type),
    path('view_owners/', views.view_owners)

]
