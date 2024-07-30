from django.shortcuts import render
from .models import User, UserRole, Roles, OTPDetails, LeftPanel
import json
from django.http import JsonResponse
from predine.constants import request_handlers, status_code, status_message, functions
from django.contrib.auth import login, authenticate, logout
import random
import threading
import secret
from django.utils import timezone


def login_user(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        validate_data = functions.validate(username=username,
                                           password=password, api_type="LOGIN")
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            role = list(UserRole.objects.filter(
                user=user).values('role_id', 'role_id__role_name'))
            print(role)
            request.session['user'] = user.id
            request.session['role'] = role[0]['role_id']
            request.session['role_name'] = role[0]['role_id__role_name']

            check_email_verified = OTPDetails.objects.filter(
                email=username).order_by('-id').first()
            if check_email_verified is not None:
                if check_email_verified.verified_status is False:
                    return JsonResponse({'msg': status_message.EMAIL_NOT_VERIFIED}, status=status_code.BAD_REQUEST)
            else:
                return JsonResponse({'msg': status_message.EMAIL_NOT_VERIFIED}, status=status_code.BAD_REQUEST)
            return JsonResponse({"msg": status_message.LOGIN})
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
        validate_data = functions.validate(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number,
                                           api_type="USER", password=password, confirm_password=confirm_password)
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)
        if confirm_password != password:
            return JsonResponse({'msg': status_message.PASSWORD_NOT_MATCH}, status=status_code.BAD_REQUEST)

        if UserRole.objects.filter(user_id__email=email, role_id__role_name='USER').exists():
            return JsonResponse({'msg': status_message.USER_ALREADY_REGISTERED}, status=status_code.BAD_REQUEST)

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
            return JsonResponse({"msg": status_message.REGISTERED})
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def send_verification_mail(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        print(data)
        email = data.get('email')
        print(email)
        if OTPDetails.objects.filter(email=email, verified_status=True).exists():
            return JsonResponse({'msg': status_message.EMAIL_ALREADY_VERIFIED}, status=status_code.BAD_REQUEST)
        validate_data = functions.validate(email=email, api_type="INITIAL REG")
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)
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
            else:
                return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def verify_otp(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        otp = data.get('otp')
        email = data.get('email')
        validate_data = functions.validate(
            email=email, otp=otp, api_type="OTP")
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

        if OTPDetails.objects.filter(otp=otp, email=email, deleted_status=False, verified_status=False).first():
            OTPDetails.objects.filter(otp=otp, email=email).update(
                verified_status=True, deleted_status=True, deleted_time=timezone.now())
            return JsonResponse({'msg': status_message.VERIFY_EMAIL})
        else:
            return JsonResponse({'msg': status_message.OTP_INVALID}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def resend_otp(request):
    if request_handlers.request_type(request, 'POST'):
        data = json.loads(request.body)
        email = data.get('email')
        OTPDetails.objects.filter(email=email).update(
            deleted_status=True, deleted_time=timezone.now())
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
            else:
                return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
        else:
            return JsonResponse({"msg": status_message.BAD_REQUEST}, status=status_code.BAD_REQUEST)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def check_email_verification(request):
    print(request.GET)
    if request_handlers.request_type(request, 'GET'):
        email = request.GET.get('email')
        print(email)
        validate_data = functions.validate(email=email, api_type="INITIAL REG")
        if validate_data is not None:
            if validate_data['status'] == True and validate_data['other'] == False:
                return JsonResponse({'msg': validate_data['msg']+' '+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            elif validate_data['status'] == True and validate_data['other'] == True:
                return JsonResponse({'msg': validate_data['msg']}, status=status_code.BAD_REQUEST)

        if UserRole.objects.filter(user_id__email=email, role_id__role_name='USER').exists():
            return JsonResponse({'msg': status_message.USER_ALREADY_REGISTERED}, status=status_code.BAD_REQUEST)

        if OTPDetails.objects.filter(email=email, verified_status=True).exists():
            return JsonResponse({'msg': status_message.SUCCESS}, status=status_code.SUCCESS)
        else:
            return JsonResponse({'msg': status_message.EMAIL_NOT_VERIFIED}, status=status_code.BAD_REQUEST)

    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def check_auth(request):
    if request_handlers.request_type(request, 'GET'):
        return JsonResponse({'msg': 'Welcome to Predine'}, status=status_code.SUCCESS)


def left_panel(request):
    if request_handlers.request_type(request, 'GET'):
        print("role", request.session['role'])
        panel_data = LeftPanel.objects.filter(role=request.session['role'], deleted_status=False, child=None).values(
            'name', 'component', 'icon', 'order', 'icon_type', 'title'
        )
        print(panel_data)
        return JsonResponse({'data': list(panel_data)}, status=status_code.SUCCESS)
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)


def logout_user(request):
    if request_handlers.request_type(request, 'GET'):
        request.session.flush()
        logout(request)
        return JsonResponse({'msg': status_message.LOGOUT})
    else:
        return JsonResponse({'msg': status_message.METHOD_NOT_ALLOWED}, status=status_code.METHOD_NOT_ALLWOED)
