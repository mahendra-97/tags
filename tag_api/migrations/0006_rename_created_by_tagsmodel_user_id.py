# Generated by Django 4.1.5 on 2023-12-27 05:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tag_api', '0005_userprofile_alter_tagsmodel_created_by'),
    ]

    operations = [
        migrations.RenameField(
            model_name='tagsmodel',
            old_name='created_by',
            new_name='user_id',
        ),
    ]
