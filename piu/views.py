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
from system_admin.models import *
from django.core.exceptions import ObjectDoesNotExist


class Dashboard(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:
            return render(request, 'piu_members/pages/dashboard.html')
        else:
            return HttpResponseRedirect(reverse('login'))

        
class DocumentRepo(View):
    def get(self, request, format=None):
        if request.user.is_authenticated:  
            context={'folders': SubFolders.objects.all().order_by('root_folder'),'doc_repo':True}
            return render(request, 'piu_members/pages/document_repo/documents.html', context )
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
            return render(request, 'piu_members/pages/document_repo/root_folders/root_folders.html', context)
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
            return render(request, 'piu_members/pages/document_repo/sub_folders/sub_folders.html', context)
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
            return render(request, 'piu_members/pages/document_repo/documents_list.html', context)
        else:
            return HttpResponseRedirect(reverse('login'))
        
                
class UpdateDocView(View):
    def get(self, request, document_uid):
        if request.user.is_authenticated:
            doc = DocumentsRepo.objects.filter(document_uid=document_uid)
            context = {'doc' : doc,'sub':True} 
            return render(request, 'piu_members/pages/document_repo/edit_document.html', context)
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
            return render(request, 'piu_members/pages/document_repo/change_doc.html', context)
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
  





  
        
        
        
        
        
        