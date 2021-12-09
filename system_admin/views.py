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
from django.core.exceptions import ObjectDoesNotExist


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

class DeleteUser(View):
    def post(self, request):
        if request.user.is_authenticated:
            person = User.objects.get(user_uid=request.POST.get('person_id'))
            person.delete()
            msg = 'User deleted successfully.'
            error_code = status.HTTP_200_OK        
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data)) 
        else:
            return HttpResponseRedirect(reverse('login'))

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
        
class DeleteDoc(View):
    def post(self, request):
        if request.user.is_authenticated:
            record = DocumentsRepo.objects.get(document_uid=request.POST.get('record_id'))
            record.delete()
            msg = 'File deleted successfully.'
            error_code = status.HTTP_200_OK        
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
    def get_roots(self):
        try:
            root_folders = RootFolders.objects.all()
            root_folders_list = root_folders
        except RootFolders.DoesNotExist:
            root_folders_list = ""
        return root_folders_list
            
    def get(self, request, format=None):
        if request.user.is_authenticated:
                
            try:
                folders = SubFolders.objects.all()
                if folders:
                    context={'folders' : folders, 'root_folders_list':self.get_roots(), 'sub':True} 
            except SubFolders.DoesNotExist:
                folders = ""
            context = {'folders' : folders,'root_folders_list':self.get_roots(), 'sub':True} 
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
    def get_roots(self,sub_folder_uid):
        sub_folde = SubFolders.objects.get(sub_folder_uid=sub_folder_uid)
        try:
            documents = DocumentsRepo.objects.get(doc_sub_folder=sub_folde.id)
            docus = documents
        except DocumentsRepo.DoesNotExist:
            docus = ""
        return docus
    
    def get(self, request, sub_folder_uid):
        if request.user.is_authenticated:
            root_folders = RootFolders.objects.all()
            sub_folder = SubFolders.objects.filter(sub_folder_uid=sub_folder_uid)
            context = {'sub_folder' : sub_folder,'root_folders':root_folders,'docus':self. get_roots(sub_folder_uid), 'sub':True} 
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
        
class DeleteSubFolder(View):
    def post(self, request):
        if request.user.is_authenticated:
            record = SubFolders.objects.get(sub_folder_uid=request.POST.get('record_id'))
            record.delete()
            msg = 'Folder deleted successfully.'
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
            sub_id = sub_folder.id
            sub_folder_users = DocumentsRepoSubRights.objects.filter(document_sub_folder = sub_id)
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
  
#Website Config  
class WebAboutView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                abt = About.objects.get(id=1)
                if abt:
                    context = {'abt' : abt,'web_ab':True} 
            except About.DoesNotExist:
                context = {'abt' : '','web_ab':True}  
            return render(request, 'system_admin/pages/web_about.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                abt = About.objects.get(id=1)
                if abt:
                    abt.about_us = request.POST.get('about_us')
                    abt.save()
                    msg = 'About Us updated successfully.'
                    error_code = status.HTTP_200_OK  
            except About.DoesNotExist:
                About.objects.create(
                about_us = request.POST.get('about_us'),
                author = self.request.user,
                )
                msg = 'About Us created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login'))      
        
class ProjectDescriptionView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                pro_desc = ProjectDescription.objects.get(id=1)
                if pro_desc:
                    context = {'pro_desc' : pro_desc,'web_pro_desc':True} 
            except ProjectDescription.DoesNotExist:
                context = {'pro_desc' : '','web_pro_desc':True}  
            return render(request, 'system_admin/pages/project_description.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                pro_desc = ProjectDescription.objects.get(id=1)
                if pro_desc:
                    pro_desc.project_description = request.POST.get('projectDescription')
                    pro_desc.save()
                    msg = 'Project Description updated successfully.'
                    error_code = status.HTTP_200_OK  
            except ProjectDescription.DoesNotExist:
                ProjectDescription.objects.create(
                project_description = request.POST.get('projectDescription'),
                author = self.request.user,
                )
                msg = 'Project Description created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login')) 


class WhereWeWorkView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                work = CoreSites.objects.get(id=1)
                if work:
                    context = {'work' : work,'www':True} 
            except CoreSites.DoesNotExist:
                context = {'work' : '','www':True}  
            return render(request, 'system_admin/pages/where_we_work.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                work = CoreSites.objects.get(id=1)
                if work:
                    work.where_we_work = request.POST.get('where_we_work')
                    work.save()
                    msg = 'Where We Work updated successfully.'
                    error_code = status.HTTP_200_OK  
            except CoreSites.DoesNotExist:
                CoreSites.objects.create(
                where_we_work = request.POST.get('where_we_work'),
                author = self.request.user,
                )
                msg = 'Where We Work created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login')) 

class CoreSitesView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                c_sites = CoreSites.objects.get(id=1)
                if c_sites:
                    context = {'c_sites' : c_sites,'coreSite':True} 
            except CoreSites.DoesNotExist:
                context = {'c_sites' : '','coreSite':True}  
            return render(request, 'system_admin/pages/core_sites.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                c_sites = CoreSites.objects.get(id=1)
                if c_sites:
                    c_sites.core_sites = request.POST.get('core_sites')
                    c_sites.save()
                    msg = 'Core Sites updated successfully.'
                    error_code = status.HTTP_200_OK  
            except CoreSites.DoesNotExist:
                CoreSites.objects.create(
                core_sites = request.POST.get('core_sites'),
                author = self.request.user,
                )
                msg = 'Core Sites created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login')) 

class ISFSitesView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                isfs = CoreSites.objects.get(id=1)
                if isfs:
                    context = {'isfs' : isfs,'isfSite':True} 
            except CoreSites.DoesNotExist:
                context = {'isfs' : '','isfSite':True}  
            return render(request, 'system_admin/pages/isf_sites.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                isfs = CoreSites.objects.get(id=1)
                if isfs:
                    isfs.isf_sites = request.POST.get('isf_sites')
                    isfs.save()
                    msg = 'ISF Sites updated successfully.'
                    error_code = status.HTTP_200_OK  
            except CoreSites.DoesNotExist:
                CoreSites.objects.create(
                isf_sites = request.POST.get('isf_sites'),
                author = self.request.user,
                )
                msg = 'ISF Sites created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login')) 

class RemedialSitesView(View):
    def get(self, request):
        if request.user.is_authenticated:
            try:
                remedial = CoreSites.objects.get(id=1)
                if remedial:
                    context = {'remedial' : remedial,'remSite':True} 
            except CoreSites.DoesNotExist:
                context = {'remedial' : '','remSite':True}  
            return render(request, 'system_admin/pages/remedial_sites.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))   
        
    def post(self, request):
        if request.user.is_authenticated: 
            try:
                remedial = CoreSites.objects.get(id=1)
                if remedial:
                    remedial.remidial_work_sites = request.POST.get('remidial_work_sites')
                    remedial.save()
                    msg = 'Remedial Sites updated successfully.'
                    error_code = status.HTTP_200_OK  
            except CoreSites.DoesNotExist:
                CoreSites.objects.create(
                remidial_work_sites = request.POST.get('remidial_work_sites'),
                author = self.request.user,
                )
                msg = 'Remedial Sites created successfully.'
                error_code = status.HTTP_201_CREATED 
            response_data = {'status' : error_code, 'msg' : msg}
            return HttpResponse(json.dumps(response_data))
        else:
            return HttpResponseRedirect(reverse('login')) 













  
        
        
        
        
        
        