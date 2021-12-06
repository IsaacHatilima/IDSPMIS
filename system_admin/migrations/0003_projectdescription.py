# Generated by Django 3.2.9 on 2021-12-03 02:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system_admin', '0002_coresitelist'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_description', models.TextField(null=True, verbose_name='Project Description')),
                ('date_created', models.DateField(auto_now=True, verbose_name='date_created')),
                ('date_modified', models.DateField(auto_now=True, verbose_name='date_modified')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='author')),
            ],
            options={
                'verbose_name': 'Project Description',
                'verbose_name_plural': 'Project Description',
                'db_table': 'project_description',
            },
        ),
    ]