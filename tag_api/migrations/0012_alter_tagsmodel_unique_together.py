# Generated by Django 4.1.5 on 2023-12-28 11:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tag_api', '0011_alter_tagsmodel_scope'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tagsmodel',
            unique_together={('tag_name', 'scope')},
        ),
    ]
