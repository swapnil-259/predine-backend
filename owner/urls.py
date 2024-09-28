from django.urls import path
from owner import views

urlpatterns = [
    path('owner_data/', views.owner_data),
    path('add_dish/', views.add_dish),
    path('get_dish_cat/', views.get_dish_type),
    path('get_diet_pref/', views.get_diet_pref),
    path('all_dish/', views.get_all_dishes),
    path('get_all_category/', views.get_all_categories),
    path('edt_res_image/',views.edit_res_image),
    path('add_bank_details/',views.add_bank_details),
    path('check_acc_status/',views.check_bank_status),
    path('view_bank_details/',views.view_bank_details),
    path('add_chef/',views.add_chef)

]
