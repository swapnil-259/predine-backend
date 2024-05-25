from django.shortcuts import render
from .models import OwnerDetails, User, UserRole, Roles, OTPDetails, Dropdown
import json
from django.http import JsonResponse
from predine.constants import request_handlers, status_code, status_message, functions
from django.contrib.auth import login, authenticate
import random
import threading
import secret


def owner_registration(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        email = data.get('email')
        phone_number = data.get('phone_number')
        restaurant_name = data.get('restaurant_name')
        address = data.get('address')
        type = data.get('type')
        role = data.get('role')
        functions.validate(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number,
                           restaurant_name=restaurant_name, address=address, role=role, type=type, api_type="OWNER")

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            password=secret.OWNER_PASS
        )

        if user:
            role = UserRole.objects.create(
                role=Roles.objects.get(id=role, deleted_status=False),
                user=user
            )

            owner = OwnerDetails.objects.create(
                restaurant_name=restaurant_name,
                address=address,
                type=Dropdown.objects.get(
                    id=type, deleted_status=False, child=1)
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
            role = list(UserRole.objects.filter(
                user=user).values('id', 'role_id__role_name'))
            print(role[0]['role_id__role_name'])
            request.session['user'] = user.id
            request.session['role'] = role[0]['id']
            request.session['role_name'] = role[0]['role_id__role_name']
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
        confirm_password = data.get('confirm_password')
        if confirm_password != password:
            return JsonResponse({'msg': status_message.PASSWORD_NOT_MATCH}, status=status_code.BAD_REQUEST)
        if OTPDetails.objects.filter(email=email, verified_status=True).exists() is False:
            return JsonResponse({'msg': status_message.EMAIL_NOT_VERIFIED}, status=status_code.BAD_REQUEST)

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            password=password,
            username=email,
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
        functions.validate(email=email, api_type="INITIAL REG")
        otp = random.randint(100000, 999999)
        otp_generate = OTPDetails.objects.create(
            email=email,
            otp=otp
        )
        if otp_generate:
            mail = functions.verification_email(email, otp)
            if mail:
                threading.Thread(
                    target=(functions.otp_expire), args=(email, otp)).start()
                return JsonResponse({'msg': status_message.OTP_SENT})
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)

        return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def verify_otp(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        otp = data.get('otp')
        email = data.get('email')
        if OTPDetails.objects.filter(otp=otp, email=email, deleted_status=False, verified_status=False).first():
            OTPDetails.objects.filter(otp=otp, email=email).update(
                verified_status=True, deleted_status=True)
            return JsonResponse({'msg': status_message.VERIFY_EMAIL})
        else:
            return JsonResponse({'msg': status_message.OTP_INVALID}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
