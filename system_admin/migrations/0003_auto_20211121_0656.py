# Generated by Django 3.2.9 on 2021-11-21 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system_admin', '0002_auto_20211121_0613'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rootfolders',
            name='root_folder_status',
            field=models.EmailField(default='Active', max_length=20, unique=True, verbose_name='Root Folder Status'),
        ),
        migrations.AlterField(
            model_name='subfolders',
            name='sub_folder_status',
            field=models.EmailField(default='Active', max_length=20, verbose_name='Sub Folder Status'),
        ),
    ]
