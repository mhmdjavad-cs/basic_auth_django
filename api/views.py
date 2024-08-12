from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.core.mail import send_mail
from .functions import send_email_verification_code
import threading
from .models import VerificationCode
from django.utils import timezone


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
        return Response({
            "status": "error",
            "message": "the username is already taken!",
        })
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
    print("the actual code is: ", real_code.verification_code)
    print("the code you privide is: ", code)
    
    if code == real_code.verification_code:
        
        if real_code.code_expires_at > timezone.now():
            token, created = Token.objects.get_or_create(user=user)
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
    
    print("im here")
    thread = threading.Thread(target=send_email_verification_code, args=(user, user.email))
    thread.start()
    
    return Response({
                        "status": "success",
                        "message": "a new code is sent to your email!",
                        })
    
    
    