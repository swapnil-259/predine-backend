from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from Login.models import OTPDetails


def verification_email(email, otp):

    context = {
        'otp': otp,
        'email': email
    }
    body = render_to_string(
        '', context)
    subject = 'OTP VERIFICATION | PREDINE'
    from_email = settings.EMAIL_HOST_USER
    to_mail = [email]
    mail = send_mail(from_email, to_mail, subject, body)
    print(mail)
    if mail:
        return True


def otp_expire(email, otp):
    OTPDetails.objects.filter(
        otp=otp, email=email, deleted_status=False).update(deleted_status=False)
