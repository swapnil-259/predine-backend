from django.urls import path
from Login import views


urlpatterns = [
    path('user_registration/', views.user_registration),
    path('login_user/', views.login_user),
    path('verification_mail/', views.send_verification_mail),
    path('otp_verification/', views.verify_otp),
    path('resend_otp/', views.resend_otp),
    path('check_email_verf/', views.check_email_verification),
    path('check_auth/', views.check_auth),
    path('left_panel/', views.left_panel),
    path('logout/', views.logout_user),
]
