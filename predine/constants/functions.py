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
    print(otp, email)

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
                     recipient_list=recipient_list, html_message=html_message)
    print("mail", mail)
    if mail:
        return True
    else:
        return False


def otp_expire(email, otp):
    time.sleep(120)

    OTPDetails.objects.filter(
        otp=otp, email=email, deleted_status=False).update(deleted_status=True, deleted_time=timezone.now())
    print("otp-deleted")


def validate(first_name=None, last_name=None, email=None, phone_number=None, restaurant_name=None, address=None, password=None, confirm_password=None, role=None, type=None, api_type=None, username=None, otp=None, parent=None, child=None):
    mobile_pattern = r'^[789]\d{9}$'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    response = {'msg': '', 'status': False, 'other': False}
    match api_type:
        case "OWNER":
            if first_name.strip() == '' or first_name == None:
                response['msg'] = 'First Name'
                response['status'] = True
                return response
            if last_name.strip() == '' or last_name == None:
                response['msg'] = 'Last Name'
                response['status'] = True
                return response
            # if email.strip() == '' or email == None:
            #     response['msg'] = 'Email'
            #     response['status'] = True
            #     return response
            if phone_number.strip() == '' or phone_number == None:
                response['msg'] = 'Phone Number'
                response['status'] = True
                return response
            if restaurant_name.strip() == '' or restaurant_name == None:
                response['msg'] = 'Restaurant Name'
                response['status'] = True
                return response
            if address.strip() == '' or address == None:
                response['msg'] = 'Address'
                response['status'] = True
                return response
            # if role.strip() == '' or role == None:
            #     response['msg'] = 'Role'
            #     response['status'] = True
            #     return response
            # if type.strip() == '' or type == None:
            #     response['msg'] = 'Type'
            #     response['status'] = True
            #     return response
            if not re.match(mobile_pattern, phone_number):
                return JsonResponse({'msg': status_message.NUMBER_INVALID}, status=status_code.BAD_REQUEST)
            # if not re.match(email_pattern, email):
            #     return JsonResponse({'msg': status_message.EMAIL_INVALID}, status=status_code.BAD_REQUEST)
        case "USER":
            if first_name.strip() == '' or first_name == None:
                response['msg'] = 'First Name'
                response['status'] = True
                return response
            if last_name.strip() == '' or last_name == None:
                response['msg'] = 'Last Name'
                response['status'] = True
                return response
            if phone_number.strip() == '' or phone_number == None:
                response['msg'] = 'Phone Number'
                response['status'] = True
                return response
            if password.strip() == '' or password == None:
                response['msg'] = 'Password'
                response['status'] = True
                return response
            if confirm_password.strip() == '' or confirm_password == None:
                response['msg'] = 'Confirm Password'
                response['status'] = True
                return response
            if password != confirm_password:
                response['msg'] = status_message.PASSWORD_NOT_MATCH
                response['other'] = True
                response['status'] = True
            # if len(password) < 8:
            #     response['msg'] = status_message.PASSWORD_CHECK
            #     response['other'] = True
            #     response['status'] = True
            #     return response
            # if not password.isalnum():
            #     response['msg'] = status_message.PASSWORD_CHECK
            #     response['other'] = True
            #     response['status'] = True
            #     return response
            if not re.match(mobile_pattern, phone_number):
                response['msg'] = status_message.NUMBER_INVALID
                response['other'] = True
                response['status'] = True
                return response
            # if not re.match(email_pattern, email):
            #     response['msg'] = status_message.EMAIL_INVALID
            #     response['other'] = True
            #     response['status'] = True
            #     return response
        case "INITIAL REG":
            print("emmm", email)
            if email == '' or email == None or len(email) == 0:
                response['msg'] = 'Email'
                response['status'] = True
                return response

            if not re.match(email_pattern, email):
                response['msg'] = status_message.EMAIL_INVALID
                response['other'] = True
                response['status'] = True
                return response

        case "LOGIN":
            if username.strip() == '' or username == None or len(username) == 0:
                response['msg'] = 'Email'
                response['status'] = True
                return response
            if password.strip() == '' or password == None:
                response['msg'] = 'Password'
                response['status'] = True
                return response
        case "OTP":
            if otp == '' or otp == None or len(otp) == 0:
                response['msg'] = 'OTP'
                response['status'] = True
                return response
            if email == '' or email == None or len(email) == 0:
                response['msg'] = 'Email'
                response['status'] = True
                return response
        case "ADD CHILD":
            if parent == '' or parent == None:
                response['msg'] = 'OTP'
                response['status'] = True
                return response
            if child == '' or child == None or len(child) == 0:
                response['msg'] = 'Email'
                response['status'] = True
                return response


def get_restaurant_img(self, filename):
    return "RES_{0}/{1}".format(self.restaurant_name, filename)


def get_dish_img(self, filename):
    return "DISH_{0}/{1}".format(self.name, filename)
