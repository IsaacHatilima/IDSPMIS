from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.Login.as_view(), name="login"),
    path('logout/', views.logsout, name="logout"),
    path('forgot-password/', views.ForgotPassword.as_view(), name="forgot_password"),
    path('account-activation', views.AccountVerification.as_view(), name="account_activation"),
    
]