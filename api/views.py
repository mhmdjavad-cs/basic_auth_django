import threading

from django.shortcuts import render
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status

from .functions import send_email_verification_code
from .models import VerificationCode



@api_view(["GET"])
def home(request):
    return Response({"hello": "this is the home view!"})


@api_view(['POST'])
def signup(request):

    try:
        username = request.data['username'] 
        password = request.data['password']
        email = request.data['email']

    except:
        return Response({"status": "error",
            "message": "all fields should be filled!"})
        
        
    if User.objects.filter(username=username).exists():
        
        user = User.objects.get(username=username)
        verificarion_code = VerificationCode.objects.get(user=user)
        if verificarion_code.is_confirmed:
        
            return Response({
                "status": "error",
                "message": "the username is already taken!",
            })
        
        else:
            thread = threading.Thread(target=send_email_verification_code, args=(user, email))
            thread.start()
    
            return Response({"status": "success",
                    "message": "email verification code is sent",})
        
        
        
    if User.objects.filter(email=email).exists():
        return Response({
            "status": "error",
            "message": "the email is already taken!"
        })    

    user = User.objects.create_user(username=username, password=password, email=email)
    
    thread = threading.Thread(target=send_email_verification_code, args=(user, email))
    thread.start()
    
    return Response({"status": "success",
                    "message": "email verification code is sent",})
    
    
    #token, created = Token.objects.get_or_create(user=user)

    #return Response({
    #                "status": "success",
    #                "message": "user created successfuly!",
    #                "token": token.key,
    #                })


@api_view(['POST'])
def confirm_code_and_get_token(request):
    try:
        code = request.data['code']
        username = request.data['username']

    except:
        return Response({"status": "error",
            "message": "send both code and the username"})


    if User.objects.filter(username=username).exists() == False:
        return Response({
            "status": "error",
            "message": "the user doesn't exist!",
        })

    user = User.objects.get(username=username)
    real_code = VerificationCode.objects.get(user=user)
    
    if code == real_code.verification_code:
        
        if real_code.code_expires_at > timezone.now():
            
            token, created = Token.objects.get_or_create(user=user)
            
            user = User.objects.get(username=username)
            Verification_code = VerificationCode.objects.get(user=user)
            Verification_code.is_confirmed = True
            Verification_code.save()
            
            return Response({
                        "status": "success",
                        "message": "user created successfuly!",
                        "token": token.key,
                        })
        
        else:
            return Response({
            "status": "error",
            "message": "the code is expired!",
        })
        
    else:
        return Response({
            "status": "error",
            "message": "the code is incorrect!",
        })



@api_view(['POST'])
def resend_verification_code(request):
    try:
        username = request.data['username']

    except:
        return Response({"status": "error",
            "message": "send the username!"})

    if User.objects.filter(username=username).exists() == False:
        return Response({
            "status": "error",
            "message": "the user doesn't exist!",
        })

    user = User.objects.get(username=username)
    
    thread = threading.Thread(target=send_email_verification_code, args=(user, user.email))
    thread.start()
    
    return Response({
                        "status": "success",
                        "message": "a new code is sent to your email!",
                        })
    
    
class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):

        try:
            username = request.data['username']

        except:
            return Response({"status": "error",
                "message": "send the username!"})
            
        if User.objects.filter(username=username).exists() == False:
            return Response({"status": "error",
                "message": "user doesn't exist!"})
            
        else:
            user = User.objects.get(username=username)
            verification_code = VerificationCode.objects.get(user=user)
            if verification_code.is_confirmed == False:
                return Response({"status": "error",
                "message": "you should first confirm your email and login after that!"})
            
            

        response = super().post(request, *args, **kwargs)

        # Custom logic after obtaining the token
        if response.status_code == status.HTTP_200_OK:
            token = Token.objects.get(key=response.data['token'])
            #token.created = timezone.now()  # Example of adding custom logic
            token.save()

        return response
    
    