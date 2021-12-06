from django.urls import path
from .views import *
from . import views

urlpatterns = [
    path('', views.Dashboard.as_view(), name="dashboard"),
    path('create-user/', CreateUser.as_view(), name="create_user"),
    path('user-list/', UsersView.as_view(), name="users"),
    #Dcument Repo
    path('document-repository/', views.DocumentRepo.as_view(), name="documents_repo"),
    path('document-repository/<sub_folder_uid>/', views.DocumentsView.as_view(), name="documents_repo_view"),
    path('document-details/<document_uid>/', views.UpdateDocView.as_view(), name="document_details"),
    path('document-details-update/', views.UpdateDocumentView.as_view(), name="update_doc_details"),
    path('document-update/<document_uid>/', views.ChangeDocView.as_view(), name="change_details"),
    path('document-file-update/', views.UploadDocumentView.as_view(), name="update_doc"),
    path('document-root-folders/', views.RootFoldersView.as_view(), name="documents_root_folders"),
    path('root-folders-details/<root_folder_uid>/', views.RootFoldersEdit.as_view(), name="documents_root_folders_dets"),
    path('root-folders-details-manged/', views.UpdateDeleteRoot.as_view(), name="documents_root_folders_mng"),
    path('document-sub-folders/', views.SubFoldersView.as_view(), name="documents_sub_folders"),
    path('sub-folders-details/<sub_folder_uid>/', views.SubFoldersEdit.as_view(), name="documents_sub_folders_dets"),
    path('sub-folders-details-manged/', views.UpdateSub.as_view(), name="documents_sub_folders_mng"),
    path('sub-folders-rights/<sub_fold_uid>/', views.DocumentsRightsView.as_view(), name="documents_sub_folders_rights"),
    path('sub-folders-rights/add', views.AddFolderUser.as_view(), name="documents_sub_folders_rights_maker"),
    path('sub-folders-rights/delete', views.DeleteFolderUser.as_view(), name="delete_folder_user"),
    path('sub-folders-rights/update', views.UpdateFolderUser.as_view(), name="update_folder_user"),
    #Website Config
    path('website-about/', views.WebAboutView.as_view(), name="web_about"),
    path('website-project-description/', views.ProjectDescriptionView.as_view(), name="project_desc"),
    path('where-we-work/', views.WhereWeWorkView.as_view(), name="where_works"),
    path('core-sites/', views.CoreSitesView.as_view(), name="core_sites"),
    path('isf-sites/', views.ISFSitesView.as_view(), name="isf_sites"),
    path('remedial-sites/', views.RemedialSitesView.as_view(), name="remedial_sites"),
    
]