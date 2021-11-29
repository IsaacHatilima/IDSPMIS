from django.shortcuts import render
from django.http import Http404,HttpResponse,HttpResponseRedirect
from django.views import View
from rest_framework.response import Response
from rest_framework import status
import json
import jwt
from django.urls import reverse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from .models import User
from nanoid import generate
from django.conf import settings 
from system_admin.utils import Util


class Login(View):
    def get(self, request, format=None):
        return render(request, 'auth/login.html')
    
    def post(self, request, format=None):
        user = authenticate(email=request.POST.get('email'), password=request.POST.get('password'))
        if user:
            if user.is_active:
                if user.is_verified:
                    auth_login(request, user)
                    data =  {
                        'status' : status.HTTP_200_OK,
                        'msg' : 'Logged in successfully.',
                        'email': user.email,
                        'full_name': user.first_name,
                        'role': user.user_role,
                    }
                else:
                    data = {'status' : status.HTTP_401_UNAUTHORIZED, 'msg' : 'Your account is not verified.'}
            else:
                data = {'status' : status.HTTP_401_UNAUTHORIZED, 'msg' : 'Your account has been disabled.'}
        else:
            data = {'status' : status.HTTP_401_UNAUTHORIZED, 'msg' : 'Invalid Email or Password.'}
        return HttpResponse(json.dumps(data))


class ForgotPassword(View):
    def get(self, request, format=None):
        return render(request, 'auth/forgot_password.html')
    
    def post(self, request, format=None):
        user = User.objects.get(email=request.POST.get('email'))
        if user:
            if user.is_active:
                plain_password = generate(size=10)
                user.set_password(plain_password)
                user.save()
                email_body ="Hello "+user.first_name+ "\n"+"Your new password is: "+ plain_password + ". Consider changing it as soon as you can."
                data = {
                        'email_to' : user.email,
                        'email_body' : email_body,
                        'email_subject' : 'Password Reset'
                    }
                Util.send_email(data)
                data = {'status' : status.HTTP_200_OK, 'msg' : 'Email with password reset instructions has be sent.'}
            else:
                data = {'status' : status.HTTP_200_OK, 'msg' : 'Email with password reset instructions has be sent.'}
        else:
            data = {'status' : status.HTTP_200_OK, 'msg' : 'Email with password reset instructions has be sent.'}
        return HttpResponse(json.dumps(data))

class AccountVerification(View):
    def get(self, request, format=None):
        user_token = request.GET.get('token')
        try:
            payload = jwt.decode(user_token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            context = {"message" : "Your Account Has Been Activated, Login To Start Your Session"}
            return render(request, 'auth/activation.html', context)
            # return Response({"data" : 'user', "message" : "User Avtivated Successfully", "status" : status.HTTP_200_OK})
        except jwt.ExpiredSignatureError as identifier:
            context = {"message" : "Your Activation Token Has Expired, Contact Your System Admin"}
            return render(request, 'auth/activation.html', context)
        except jwt.exceptions.DecodeError as identifier:
            context = {"message" : "Invalid Token"}
            return render(request, 'auth/activation.html', context)   
            

def logsout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))

