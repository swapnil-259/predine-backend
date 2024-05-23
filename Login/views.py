from django.shortcuts import render
from .models import OwnerDetails, User, UserRole, Roles, OTPDetails
import json
from django.http import JsonResponse
from predine.constants import request_handlers, status_code, status_message, functions
from django.contrib.auth import login, authenticate
import random
import time


def owner_registration(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        restaurant_name = data.get('restaurant_name')
        address = data.get('address')
        password = data.get('password')
        type = data.get('type')
        role = data.get('role')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=password
        )

        if user:
            role = UserRole.objects.create(
                role=Roles.objects.get(role_name=role),
                user=user
            )

            owner = OwnerDetails.objects.create(
                restaurant_name=restaurant_name,
                address=address,
                type=type
            )
        else:
            return JsonResponse({"msg": status_code.BAD_REQUEST}, status=status_message.BAD_REQUEST)
        if owner:
            return JsonResponse({"msg": status_message.SUCCESS})
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def login_user(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        print(user)
        if user is not None:
            login(request, user)
            role = UserRole.objects.filter(
                user=user).values('id', 'role_id__role_name')
            print(role)
            request.session['user'] = user.id
            # request.session['role'] = role
            # request.session['role_name'] = role
            return JsonResponse({"msg": status_message.SUCCESS})
        else:
            return JsonResponse({"msg": status_message.WRONG_CREDENTIALS}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def user_registration(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        password = data.get('password')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            email=email
        )
        if user:
            role = UserRole.objects.create(
                role=Roles.objects.get(role_name='USER'),
                user=user
            )
        else:
            return JsonResponse({"msg": status_code.BAD_REQUEST}, status=status_message.BAD_REQUEST)
        if role:
            return JsonResponse({"msg": status_message.VERIFY_EMAIL})
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def send_verification_mail(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        email = data.get('email')
        otp = random.random(100000, 999999)
        otp_generate = OTPDetails.objects.create(
            email=email,
            otp=otp
        )
        if otp_generate:
            mail = functions.verification_email(email, otp)
            if mail:
                time.sleep(functions.otp_expire(email, otp))
                return JsonResponse({'msg': status_message.OTP_SENT})
            return
        return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def verify_otp(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        otp = data.get('otp')
        email = data.get('email')
        if OTPDetails.objects.filter(otp=otp, email=email, deleted_status=False, verified_status=False).first():
            OTPDetails.objects.update(
                verified_status=True, deleted_status=True)
            return JsonResponse({'msg': status_message.VERIFY_EMAIL})
        else:
            return JsonResponse({'msg': status_message.OTP_INVALID}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
