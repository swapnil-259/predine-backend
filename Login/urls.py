from django.urls import path
from .views import *
url_pattern = [
    path('user_registration/', user_registration),
    path('owner_registration/', owner_registration),
    path('login/', login_user),
    path('verification_mail/', send_verification_mail),
    path('otp_verification/', verify_otp),
]
