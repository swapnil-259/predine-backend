from django.urls import path
from owner import views

urlpatterns = [
    path('owner_data/', views.owner_data),
    path('add_dish/', views.add_dish),
    path('get_dish_cat/', views.get_dish_type),
    path('get_diet_pref/', views.get_diet_pref),
    path('all_dish/', views.get_all_dishes),
    path('get_all_category/', views.get_all_categories),
    path('change_res_pic/', views.change_restaurant_pic)

]
