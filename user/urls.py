from django.urls import path
from user import views

urlpatterns=[
    path('all_restaurants/', views.get_all_restaurants),
    path('user_data/',views.get_user_data),
    path('menu_data/',views.get_menu)

]