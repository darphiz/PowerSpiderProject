# Generated by Django 4.1.5 on 2023-01-18 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pledge_app', '0004_ngo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pledgeindexedurl',
            name='locked',
            field=models.BooleanField(default=False),
        ),
    ]