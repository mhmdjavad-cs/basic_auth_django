from django.core.mail import send_mail
from random import randint
from .models import VerificationCode
from django.utils import timezone

def send_email_verification_code(user, email):
    
    code = randint(100000,999999)
    print("the code: ", code)
    print(user.username)
    if VerificationCode.objects.filter(user=user).exists():
        print('already exists:')
        verification_code = VerificationCode.objects.get(user=user)
        verification_code.verification_code = str(code)
        verification_code.code_expires_at = timezone.now() + timezone.timedelta(minutes=2)
        verification_code.save()
    else:
        print("creating a new one:")
        verification_code, created = VerificationCode.objects.update_or_create(user=user, verification_code=str(code), code_expires_at=timezone.now() + timezone.timedelta(minutes=2))
        verification_code.save()
    
    
    send_mail("verification code", str(code), "mhmdjavad.safi@gmail.com", [str(email)], fail_silently=False)



