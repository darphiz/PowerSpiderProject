# Generated by Django 4.1.5 on 2023-01-18 18:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pledge_app', '0005_pledgeindexedurl_locked'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ngo',
            name='image',
            field=models.TextField(max_length=200, null=True),
        ),
    ]
