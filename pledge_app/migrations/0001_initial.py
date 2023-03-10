# Generated by Django 4.1.5 on 2023-01-18 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CrawlCursor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('increment', models.IntegerField(default=5)),
                ('current_cursor', models.IntegerField(default=1)),
                ('max_cursor', models.IntegerField(default=20)),
            ],
        ),
        migrations.CreateModel(
            name='PledgeIndexedUrl',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=200, unique=True)),
                ('is_scraped', models.BooleanField(default=False)),
                ('added_on', models.DateTimeField(auto_now=True)),
                ('scraped_on', models.DateTimeField(null=True)),
                ('crawler', models.CharField(max_length=100, null=True)),
            ],
        ),
    ]