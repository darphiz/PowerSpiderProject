# Generated by Django 4.1.5 on 2023-05-19 07:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merger', '0008_alter_uniquengo_unique_together_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='uniquengo',
            name='primary_first_name',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='uniquengo',
            name='primary_last_name',
            field=models.CharField(max_length=200, null=True),
        ),
    ]