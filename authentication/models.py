from django.db import models
from django.urls import reverse
from django.contrib.auth.models import(AbstractBaseUser, BaseUserManager, PermissionsMixin)
import uuid
from rest_framework_simplejwt.tokens import RefreshToken

class UserManager(BaseUserManager):
    def create_user(self, email,first_name,last_name,user_role,is_superuser,password=None):
        if email is None:
            raise TypeError('User MUST an Email')
        user = self.model(email=email,first_name=first_name,last_name=last_name,user_role=user_role,is_superuser=is_superuser)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_uid            = models.UUIDField(verbose_name='User UID', null=False, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    email               = models.EmailField(max_length=255, verbose_name='Email', unique=True, null=False)
    first_name          = models.CharField(max_length=100, verbose_name='First Name', null=False, db_index=True)
    last_name           = models.CharField(max_length=100, verbose_name='Last Name', null=False)
    is_superuser        = models.BooleanField(verbose_name= "Is Super User",default=False)
    is_active           = models.BooleanField(verbose_name= "Is Active",default=True)
    is_verified         = models.BooleanField(verbose_name= "Is Verified",default=False)
    user_role           = models.CharField(verbose_name= "Role",max_length=50, null=True)
    date_created        = models.DateTimeField(verbose_name= "Date Created", auto_now=True, null=False)
    last_login          = models.DateTimeField(verbose_name= "Last Login", null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name','is_superuser', 'user_role']

    objects = UserManager()

    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
    def get_user_id(self):
        return self.id
   
    def get_full_name(self):
        return self.first_name + ' ' + self.last_name
    
    def get_uuid(self):
        return self.uuid

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh' : str(refresh),
            'access' : str(refresh.access_token)
        }
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"

