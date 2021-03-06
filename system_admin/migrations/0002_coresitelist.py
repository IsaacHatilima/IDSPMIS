# Generated by Django 3.2.9 on 2021-12-03 01:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreSiteList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lusitu', models.TextField(null=True, verbose_name='Lusitu')),
                ('mwomboshi', models.TextField(null=True, verbose_name='Mwomboshi')),
                ('musakashi', models.TextField(null=True, verbose_name='Musakashi')),
                ('date_created', models.DateField(auto_now=True, verbose_name='date_created')),
                ('date_modified', models.DateField(auto_now=True, verbose_name='date_modified')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Author')),
            ],
            options={
                'verbose_name': 'Safe Guard',
                'verbose_name_plural': 'Safe Guards',
                'db_table': 'safeguard_sites',
            },
        ),
    ]
