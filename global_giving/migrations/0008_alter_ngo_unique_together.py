# Generated by Django 4.1.5 on 2023-04-12 21:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('global_giving', '0007_v2globalgivingindexedurl_delete_globalgivingngo_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ngo',
            unique_together={('organization_name', 'state')},
        ),
    ]
