# Generated by Django 4.1.5 on 2023-02-12 00:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irs_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='irsindexedurl',
            name='trial',
            field=models.IntegerField(default=0),
        ),
    ]