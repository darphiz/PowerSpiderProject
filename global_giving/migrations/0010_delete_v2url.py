# Generated by Django 4.1.5 on 2023-04-12 22:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_giving', '0009_v2url_delete_v2globalgivingindexedurl'),
    ]

    operations = [
        migrations.DeleteModel(
            name='V2Url',
        ),
    ]