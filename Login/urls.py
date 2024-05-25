from django.urls import path
from Login import views


urlpatterns = [
    path('user_registration/', views.user_registration),
    path('owner_registration/', views.owner_registration),
    path('login_user/', views.login_user),
    path('verification_mail/', views.send_verification_mail),
    path('otp_verification/', views.verify_otp),
]
