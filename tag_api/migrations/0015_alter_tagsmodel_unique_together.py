# Generated by Django 4.1.5 on 2023-12-28 12:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tag_api', '0014_alter_tagsmodel_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tagsmodel',
            unique_together={('tag_name', 'scope')},
        ),
    ]
