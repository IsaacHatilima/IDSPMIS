from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name="piu_dashboard"),
    #Dcument Repo
    path('document-repository/', views.DocumentRepo.as_view(), name="documents_repo"),
    path('document-root-folders/', views.RootFoldersView.as_view(), name="documents_root_folders"),
    path('document-sub-folders/', views.SubFoldersView.as_view(), name="documents_sub_folders"),
    path('document-repository/<sub_folder_uid>/', views.DocumentsView.as_view(), name="documents_repo_view"),
    path('document-details/<document_uid>/', views.UpdateDocView.as_view(), name="document_details"),
    path('document-details-update/', views.UpdateDocumentView.as_view(), name="update_doc_details"),
    path('document-update/<document_uid>/', views.ChangeDocView.as_view(), name="change_details"),
    path('document-file-update/', views.UploadDocumentView.as_view(), name="update_doc"),
    
    
    
    
    
   
    
    
]