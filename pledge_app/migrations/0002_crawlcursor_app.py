# Generated by Django 4.1.5 on 2023-01-18 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pledge_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='crawlcursor',
            name='app',
            field=models.CharField(default='error', max_length=100),
            preserve_default=False,
        ),
    ]