from django.urls import path
from .views import home, signup, confirm_code_and_get_token, resend_verification_code, CustomAuthToken

urlpatterns = [
    path('auth/login', CustomAuthToken.as_view(), name="login"),
    path('auth/signup', signup, name="signup"),
    
    path('auth/confirm_code_and_get_token', confirm_code_and_get_token, name="conform_code_and_get_token"),
    
    path('auth/resend_verification_code', resend_verification_code, name="resend_verification_code"),
    
    path('', home ,name="home"),    
]



