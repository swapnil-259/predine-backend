from django.urls import path

from user import views

urlpatterns = [
    path("all_restaurants/", views.get_all_restaurants),
    path("user_data/", views.get_user_data),
    path("menu_data/", views.get_menu),
    path("place_order/", views.place_order),
    path("order_summary/", views.get_user_orders),
    path("create_order/", views.create_order),
    path("confirm_payment/", views.confirm_payment),
    path('privacy-policy/', views.show_privacy_policy, name='privacy_policy'),
    path("cancel-order/", views.cancel_order),
    path('account-delete/',views.request_account_deletion),
    # path('order-cancelled-no-owner-response/',views.order_cancelled_no_owner_response),
]
