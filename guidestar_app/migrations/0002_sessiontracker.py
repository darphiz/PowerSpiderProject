# Generated by Django 4.1.5 on 2023-02-10 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guidestar_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionTracker',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cookies', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]