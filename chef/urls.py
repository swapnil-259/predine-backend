from django.urls import path
from chef import views

urlpatterns = [
    path('chef_orders/', views.chef_orders),
    path('order_completed/',views.complete_order),
    path('order_recieved/',views.receive_order)

]
