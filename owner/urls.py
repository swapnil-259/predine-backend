from django.urls import path
from owner import views

urlpatterns = [
    path('owner_data/', views.owner_data),
    path('add_dish/', views.add_dish),
    path('get_dish_cat/', views.get_dish_type)
]
