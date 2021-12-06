from django.db import models
import uuid
from django.urls import reverse
from authentication.models import User

##########################Document Repository
class RootFolders(models.Model):
    root_folder_uid         = models.UUIDField(verbose_name='Root Folder UID', null=False, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    root_folder_name        = models.CharField(max_length=255, verbose_name='Root Folder Name', unique=True, blank=False, null=False)
    root_folder_status      = models.CharField(max_length=20, verbose_name='Root Folder Status', default="Active",blank=False, null=False)
    created_by              = models.ForeignKey(User, verbose_name = "Created By", on_delete=models.CASCADE)
    date_created            = models.DateTimeField(verbose_name= "Date Created", auto_now=True, null=False)


    def __str__(self):
        return self.root_folder_name
    
    def get_uuid(self):
        return self.root_folder_uid
    
    def get_absolute_url(self):
        return reverse('documents_root_folders_dets', kwargs={'root_folder_uid' : self.root_folder_uid})
    
    class Meta:
        db_table = "root_folders"
        verbose_name = "Root Folder"
        verbose_name_plural = "Root Folders"
        
class SubFolders(models.Model):
    root_folder        = models.ForeignKey(RootFolders, verbose_name = "Root Folder", on_delete=models.CASCADE, related_name = "root_folder")
    sub_folder_uid     = models.UUIDField(verbose_name='Sub Folder UID', null=False, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    sub_folder_name    = models.CharField(max_length=255, verbose_name='Sub Folder Name', unique=True, blank=False, null=False)
    sub_folder_status  = models.CharField(max_length=20, verbose_name='Sub Folder Status', default="Active", blank=False, null=False)
    created_by         = models.ForeignKey(User, verbose_name = "Created By", on_delete=models.CASCADE)
    date_created       = models.DateTimeField(verbose_name= "Date Created", auto_now=True, null=False)

    def __str__(self):
        return self.sub_folder_name
    

    def get_uuid(self):
        return self.sub_folder_uid
    
    def get_absolute_url(self):
        return reverse('documents_sub_folders_dets', kwargs={'sub_folder_uid' : self.sub_folder_uid})
    
    def get_absolute_url_for_view(self):
        return reverse('documents_repo_view', kwargs={'sub_folder_uid' : self.sub_folder_uid})
    
    class Meta:
        db_table = "sub_folders"
        verbose_name = "Sub Folder"
        verbose_name_plural = "Sub Folders"


class DocumentsRepo(models.Model):
    doc_root_folder     = models.ForeignKey(RootFolders, verbose_name = "Root Folder", on_delete=models.CASCADE)
    doc_sub_folder      = models.ForeignKey(SubFolders, verbose_name = "Sub Folder", on_delete=models.CASCADE)
    document_uid        = models.UUIDField(verbose_name='Document UID', null=False, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    document_name       = models.CharField(max_length=255, verbose_name='Document Name', unique=True, blank=False, null=False)
    disclosure          = models.CharField(verbose_name="Disclosure",max_length=50, null=False)
    document_path       = models.FileField(upload_to='mis_doc_repo/')
    created_by          = models.ForeignKey(User, verbose_name = "Created By", on_delete=models.CASCADE)
    date_created        = models.DateTimeField(verbose_name= "Date Created", auto_now=True, null=False)
    
    def __str__(self):
        return self.document_name
    
    def get_absolute_url(self):
        return reverse('document_details', kwargs={'document_uid' : self.document_uid})

    def get_doc_absolute_url(self):
        return reverse('change_details', kwargs={'document_uid' : self.document_uid})

    def get_absolute_url_for_all(self):
        return reverse('documents_repo_view', kwargs={'sub_folder_uid' : self.sub_folder_uid})
    
    class Meta:
        db_table = "document_repo"
        verbose_name = "DocumentRepository"
        verbose_name_plural = "DocumentRepositorys"
        
class DocumentsRepoSubRights(models.Model):
    right_uid               = models.UUIDField(verbose_name='Right UID', null=False, default=uuid.uuid4, editable=False, unique=True, db_index=True)
    rights_to               = models.ForeignKey(User, verbose_name = "Rights To", on_delete=models.CASCADE)
    document_sub_folder     = models.ForeignKey(SubFolders, verbose_name = "Sub Folder", on_delete=models.CASCADE)
    document_right          = models.CharField(max_length=255, verbose_name='Document Right', blank=False, null=False)
    
    def __str__(self):
        return self.document_right
    
    def get_absolute_url(self):
        return reverse('documents_sub_folders_rights', kwargs={'sub_folder_uid' : self.sub_folder_uid})
    
    class Meta:
        db_table = "document_repo_rights"
        verbose_name = "Document Repository Rights"
        verbose_name_plural = "Document Repositorys Rights"
 
        
##########################Website COntent       
class About(models.Model):
    
    author = models.ForeignKey(User, verbose_name = "Author", on_delete=models.CASCADE)
    about_us = models.TextField(verbose_name = "About Us", null=True)
    date_created = models.DateField(verbose_name= "date_created", auto_now=True)
    date_modified = models.DateField(verbose_name= "date_modified", auto_now=True)

    def __str__(self):
        return self.about_us

    class Meta:
        db_table = "about_us"
        verbose_name = "About Us"
        verbose_name_plural = "About Us"
        
class ProjectDescription(models.Model):
    
    author = models.ForeignKey(User, verbose_name = "Author", on_delete=models.CASCADE)
    project_description = models.TextField(verbose_name = "Project Description", null=True)
    date_created = models.DateField(verbose_name= "date_created", auto_now=True)
    date_modified = models.DateField(verbose_name= "date_modified", auto_now=True)

    
    def __str__(self):
        return self.project_description

    class Meta:
        db_table = "project_description"
        verbose_name = "Project Description"
        verbose_name_plural = "Project Description"

class CoreSites(models.Model):
    
    author = models.ForeignKey(User, verbose_name = "Author", on_delete=models.CASCADE)
    where_we_work = models.TextField(verbose_name = "Where We Work", null=True)
    core_sites = models.TextField(verbose_name = "Core Sites", null=True)
    isf_sites = models.TextField(verbose_name = "ISF Sites", null=True)
    remidial_work_sites = models.TextField(verbose_name = "Remidial Works Sites", null=True)
    date_created = models.DateField(verbose_name= "date_created", auto_now=True)

    def __str__(self):
        return self.where_we_work
    
    class Meta:
        db_table = "where_we_work"
        verbose_name = "Core Site"
        verbose_name_plural = "Core Sites"

            
class CoreSiteList(models.Model):
    
    author = models.ForeignKey(User, verbose_name = "Author", on_delete=models.CASCADE)
    lusitu = models.TextField(verbose_name = "Lusitu", null=True)
    mwomboshi = models.TextField(verbose_name = "Mwomboshi", null=True)
    musakashi = models.TextField(verbose_name = "Musakashi", null=True)
    date_created = models.DateField(verbose_name= "date_created", auto_now=True)
    date_modified = models.DateField(verbose_name= "date_modified", auto_now=True)

    
    def __str__(self):
        return self.lusitu

    class Meta:
        db_table = "safeguard_sites"
        verbose_name = "Safe Guard"
        verbose_name_plural = "Safe Guards"
