from django.shortcuts import render
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.response import Response
from rest_framework import status
import requests
import json
from django.contrib.sites.shortcuts import get_current_site
import secrets
from django.urls import reverse
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken
from authentication.models import User
from .utils import Util
from .models import *


class Dashboard(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            return render(request, 'system_admin/pages/dashboard.html')
        else:
            return HttpResponseRedirect(reverse('login'))
    
class CreateUser(View):
    def get(self, request, format=None):
        if request.user.is_authenticated: 
            return render(request, 'system_admin/pages/create_user.html', context={'create_user' : True})
        else:
            return HttpResponseRedirect(reverse('login'))
    def post(self, request):
        if request.user.is_authenticated: 
            email = request.POST.get('email')
            try:
                person = User.objects.get(email=email)
                msg = 'Email Address Already In Use.'
                error_code = status.HTTP_409_CONFLICT
            except User.DoesNotExist:
                role = request.POST.get('role'),
                if role == 'System Admin':
                    is_admin = True
                else:
                    is_admin = False
                plain_password = secrets.token_urlsafe(10)
                User.objects.create_user(
                    first_name = request.POST.get('first_name'),
                    last_name = request.POST.get('last_name'),
                    email = request.POST.get('email'),
                    password = plain_password,
                    user_role = request.POST.get('user_role'),
                    is_superuser = is_admin,
                )
                user = User.objects.get(email=request.POST.get('email'))
                token = RefreshToken.for_user(user).access_token
                current_site = get_current_site(request).domain
                relative_link = reverse('account_activation')
                absurl = 'http://'+current_site+relative_link+"?token="+str(token)
                email_body = 'Hi '+user.first_name+', your IDSP MIS account has been created. Use the Password: '+plain_password+' to login but first verify you account by clicking the link below \n'+'Link: '+absurl
                data = {
                    'email_to' : user.email,
                    'email_body' : email_body,
                    'email_subject' : 'Account Verification'
                }
                Util.send_email(data)
                msg = 'User created successfully.'
                error_code = status.HTTP_201_CREATED        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 

        else:
            return HttpResponseRedirect(reverse('authentication:login'))

class UsersView(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:  
            user_list = User.objects.all()
            context={'user_list': user_list,'users':True}
            return render(request, 'system_admin/pages/users.html', context )
        else:
            return HttpResponseRedirect(reverse('login'))
        
class DocumentRepo(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:  
            context={'folders': SubFolders.objects.all().order_by('root_folder'),'doc_repo':True}
            return render(request, 'system_admin/pages/document_repo/documents.html', context )
        else:
            return HttpResponseRedirect(reverse('login'))
    def post(self, request):
        if request.user.is_authenticated:
            file = request.FILES.get('docu', None)
            DocumentsRepo.objects.create(
                doc_root_folder = RootFolders.objects.get(id=request.POST.get('doc_root_folder')),
                doc_sub_folder = SubFolders.objects.get(id=request.POST.get('doc_sub_folder')),
                document_name = request.POST.get('document_name'),
                disclosure = request.POST.get('disclosure'),
                document_path = file,
                created_by = self.request.user
            )
            msg = 'File uploaded successfully.'
            error_code = status.HTTP_201_CREATED        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login')) 
        
class RootFoldersView(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            try:
                folders = RootFolders.objects.all()
                if folders:
                    context={'folders' : folders,'roots':True} 
            except RootFolders.DoesNotExist:
                folders = ""
            context = {'folders' : folders,'roots':True} 
            return render(request, 'system_admin/pages/document_repo/root_folders/root_folders.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    def post(self, request):
        if request.user.is_authenticated:
            try:
                folders = RootFolders.objects.get(root_folder_name=request.POST.get('root_folder_name'))
                msg = 'Folder Already Exists'
                error_code = status.HTTP_409_CONFLICT
            except RootFolders.DoesNotExist:
                RootFolders.objects.create(
                    root_folder_name = request.POST.get('root_folder_name'),
                    created_by = self.request.user,
                )
                msg = 'Folder created successfully.'
                error_code = status.HTTP_201_CREATED        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))    

class RootFoldersEdit(View):
    def get(self, request, root_folder_uid):
        if request.user.is_authenticated:
            root_folder = RootFolders.objects.filter(root_folder_uid=root_folder_uid)
            context = {'root_folder' : root_folder,'roots':True} 
            return render(request, 'system_admin/pages/document_repo/root_folders/edit_folder.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
        
class UpdateDeleteRoot(View):
    def post(self, request):
        if request.user.is_authenticated:
            folders = RootFolders.objects.get(root_folder_uid=request.POST.get('root_folder_uid'))
            folders.root_folder_name=request.POST.get('root_folder_name')
            folders.root_folder_status=request.POST.get('root_folder_status')
            folders.save()
            msg = 'Folder Details Updated'
            error_code = status.HTTP_200_OK      
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))  
        
class SubFoldersView(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            try:
                root_folders = RootFolders.objects.all()
                if root_folders:
                    root_folders_list = root_folders
            except RootFolders.DoesNotExist:
                root_folders_list = ""
                
            try:
                folders = SubFolders.objects.all()
                if folders:
                    context={'folders' : folders, 'root_folders_list':root_folders_list, 'sub':True} 
            except SubFolders.DoesNotExist:
                folders = ""
            context = {'folders' : folders,'root_folders_list':root_folders_list, 'sub':True} 
            return render(request, 'system_admin/pages/document_repo/sub_folders/sub_folders.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
    def post(self, request):
        if request.user.is_authenticated:
            try:
                folders = SubFolders.objects.get(sub_folder_name=request.POST.get('sub_folder_name'))
                msg = 'Folder Already Exists'
                error_code = status.HTTP_409_CONFLICT
            except SubFolders.DoesNotExist:
                SubFolders.objects.create(
                    root_folder = RootFolders.objects.get(id=request.POST.get('root_folder')),
                    sub_folder_name = request.POST.get('sub_folder_name'),
                    created_by = self.request.user,
                )
                msg = 'Folder created successfully.'
                error_code = status.HTTP_201_CREATED        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))         
 
class SubFoldersEdit(View):
    def get(self, request, sub_folder_uid):
        if request.user.is_authenticated:
            root_folders = RootFolders.objects.all()
            sub_folder = SubFolders.objects.filter(sub_folder_uid=sub_folder_uid)
            context = {'sub_folder' : sub_folder,'root_folders':root_folders,'sub':True} 
            return render(request, 'system_admin/pages/document_repo/sub_folders/edit_folder.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
        
class UpdateSub(View):
    def post(self, request):
        if request.user.is_authenticated:
            folders = SubFolders.objects.get(sub_folder_uid=request.POST.get('sub_folder_uid'))
            folders.root_folder=RootFolders.objects.get(id=request.POST.get('root_folder'))
            folders.sub_folder_name=request.POST.get('sub_folder_name')
            folders.sub_folder_status=request.POST.get('sub_folder_status')
            folders.save()
            msg = 'Folder Details Updated'
            error_code = status.HTTP_200_OK      
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))          
        
class DocumentsView(View):
    def get(self, request, sub_folder_uid):
        if request.user.is_authenticated:
            sub = SubFolders.objects.get(sub_folder_uid=sub_folder_uid)
            sub_id = sub.id
            sub_folder = SubFolders.objects.filter(sub_folder_uid=sub_folder_uid)
            try:
                access = DocumentsRepoSubRights.objects.get(rights_to=self.request.user, document_sub_folder=sub_id)
            except DocumentsRepoSubRights.DoesNotExist:
                access = ''
            doc_file = DocumentsRepo.objects.filter(doc_sub_folder=sub_id)
            context = {'sub_folder' : sub_folder,'doc_file' : doc_file, 'access':access,'doc_repo':True} 
            return render(request, 'system_admin/pages/document_repo/documents_list.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
        
class DocumentsRightsView(View):
    def get(self, request, sub_fold_uid):
        if request.user.is_authenticated:
            sub_folder = SubFolders.objects.get(sub_folder_uid=sub_fold_uid)
            sub_folder_users = DocumentsRepoSubRights.objects.all()
            context = {'sub_folder' : sub_folder,'sub_folder_users' : sub_folder_users,'sub':True} 
            return render(request, 'system_admin/pages/document_repo/documents_rights.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))

        
class AddFolderUser(View):
    def post(self, request):
        if request.user.is_authenticated:
            person = User.objects.get(email=request.POST.get('email'))
            sub = SubFolders.objects.get(sub_folder_uid=request.POST.get('document_sub_folder'))
            DocumentsRepoSubRights.objects.create(
                document_sub_folder = sub,
                document_right = request.POST.get('document_right'),
                rights_to = person,
            )
            email_body = 'Hi '+person.first_name+',\n You have been granted: '+request.POST.get('document_right')+' rights to the '+sub.sub_folder_name+' under '+sub.root_folder.root_folder_name+'. Login to read and upload files \n The IDSP Team'
            data = {
                'email_to' : person.email,
                'email_body' : email_body,
                'email_subject' : 'Document Repository Rights'
            }
            Util.send_email(data)
            msg = 'User added successfully.'
            error_code = status.HTTP_201_CREATED        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))
        
class DeleteFolderUser(View):
    def post(self, request):
        if request.user.is_authenticated:
            record = DocumentsRepoSubRights.objects.get(id=request.POST.get('record_id'))
            record.delete()
            msg = 'User deleted successfully.'
            error_code = status.HTTP_200_OK        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))
        
class UpdateFolderUser(View):
    def post(self, request):
        if request.user.is_authenticated:
            record = DocumentsRepoSubRights.objects.get(id=request.POST.get('record_id'))
            record.document_right=request.POST.get('right')
            record.save()
            msg = 'User Rights Updated'
            error_code = status.HTTP_200_OK      
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))
        
        
class UpdateDocView(View):
    def get(self, request, document_uid):
        if request.user.is_authenticated:
            doc = DocumentsRepo.objects.filter(document_uid=document_uid)
            context = {'doc' : doc,'sub':True} 
            return render(request, 'system_admin/pages/document_repo/edit_document.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))      
        
class UpdateDocumentView(View):
    def post(self, request):
        if request.user.is_authenticated:
            record = DocumentsRepo.objects.get(document_uid=request.POST.get('document_uid'))
            record.document_name=request.POST.get('document_name')
            record.disclosure=request.POST.get('disclosure')
            record.save()
            msg = 'Document details updated'
            error_code = status.HTTP_200_OK      
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))           
        
class ChangeDocView(View):
    def get(self, request, document_uid):
        if request.user.is_authenticated:
            doc = DocumentsRepo.objects.filter(document_uid=document_uid)
            context = {'doc' : doc,'sub':True} 
            return render(request, 'system_admin/pages/document_repo/change_doc.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))         
        
class UploadDocumentView(View):
    def post(self, request):
        if request.user.is_authenticated:
            file = request.FILES.get('docu', None)
            record = DocumentsRepo.objects.get(id=request.POST.get('document_id'))
            record.document_path = file
            record.save()
            msg = 'Document Updated'
            error_code = status.HTTP_200_OK      
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))        
        
        
        
        
        
        
        
        
        