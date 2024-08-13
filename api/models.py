from django.db import models
from django.contrib.auth.models import User

from django.conf import settings

#class Profile(models.Model):
#    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    email_confirmed = models.BooleanField(default=False)


class VerificationCode(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    code_expires_at = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

