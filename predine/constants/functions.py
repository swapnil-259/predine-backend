from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
import secret
from Login.models import OTPDetails
import time
from django.utils import timezone
from django.http import JsonResponse
from predine.constants import status_code, status_message
import re


def verification_email(email, otp):

    context = {
        'otp': otp,
    }
    html_message = render_to_string(
        'email/send_otp.html', context)
    message = 'OTP verification from Predine'
    subject = 'OTP VERIFICATION | PREDINE'
    from_email = secret.EMAIL_USER
    recipient_list = [email]
    mail = send_mail(subject, message, from_email,
                     recipient_list == recipient_list, html_message=html_message)
    print("mail", mail)
    if mail:
        return True


def otp_expire(email, otp):
    print(otp)
    time.sleep(120)

    OTPDetails.objects.filter(
        otp=otp, email=email, deleted_status=False).update(deleted_status=True, deleted_time=timezone.now())
    print("otp-deleted")


def validate(first_name, last_name, email, phone_number, restaurant_name, address, password, confirm_password, role, type, api_type):
    mobile_pattern = r'^[789]\d{9}$'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    match api_type:
        case "OWNER":

            if first_name.strip() == '' or first_name == None:
                return JsonResponse({'msg': 'first name'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if last_name.strip() == '' or last_name == None:
                return JsonResponse({'msg': 'last name'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if email.strip() == '' or email == None:
                return JsonResponse({'msg': 'email'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if phone_number.strip() == '' or phone_number == None:
                return JsonResponse({'msg': 'phone number'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if restaurant_name.strip() == '' or restaurant_name == None:
                return JsonResponse({'msg': 'restaurant name'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if address.strip() == '' or address == None:
                return JsonResponse({'msg': 'address'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if role.strip() == '' or role == None:
                return JsonResponse({'msg': 'role'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if type.strip() == '' or type == None:
                return JsonResponse({'msg': 'owner type'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if not re.match(mobile_pattern, phone_number):
                return JsonResponse({'msg': status_message.NUMBER_INVALID}, status=status_code.BAD_REQUEST)
            if not re.match(email_pattern, email):
                return JsonResponse({'msg': status_message.EMAIL_INVALID}, status=status_code.BAD_REQUEST)
        case "USER":
            if first_name.strip() == '' or first_name == None:
                return JsonResponse({'msg': 'first name'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if last_name.strip() == '' or last_name == None:
                return JsonResponse({'msg': 'last name'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if phone_number.strip() == '' or phone_number == None:
                return JsonResponse({'msg': 'phone number'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if password.strip() == '' or password == None:
                return JsonResponse({'msg': 'phone number'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if confirm_password.strip() == '' or confirm_password == None:
                return JsonResponse({'msg': 'phone number'+status_message.REQUIRED}, status=status_code.BAD_REQUEST)
            if password != confirm_password:
                return JsonResponse({'msg': status_message.PASSWORD_NOT_MATCH}, status=status_code.BAD_REQUEST)
            if len(password) < 8:
                return JsonResponse({'msg': status_message.PASSWORD_CHECK}, status=status_code.BAD_REQUEST)
            if not password.isalnum():
                return JsonResponse({'msg': status_message.PASSWORD_CHECK}, status=status_code.BAD_REQUEST)
            if not re.match(mobile_pattern, phone_number):
                return JsonResponse({'msg': status_message.NUMBER_INVALID}, status=status_code.BAD_REQUEST)
            if not re.match(email_pattern, email):
                return JsonResponse({'msg': status_message.EMAIL_INVALID}, status=status_code.BAD_REQUEST)
        case "INITIAL REG":
            if not re.match(email_pattern, email):
                return JsonResponse({'msg': status_message.EMAIL_INVALID}, status=status_code.BAD_REQUEST)
