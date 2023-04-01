# Generated by Django 4.1.5 on 2023-03-30 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irs_app', '0009_alter_ngo_organization_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='NGO_V2',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organization_name', models.CharField(max_length=200, unique=True)),
                ('organization_address', models.CharField(max_length=500)),
                ('country', models.CharField(max_length=200, null=True)),
                ('state', models.CharField(max_length=200, null=True)),
                ('cause', models.TextField(null=True)),
                ('email', models.CharField(max_length=200, null=True)),
                ('phone', models.CharField(max_length=200, null=True)),
                ('website', models.CharField(max_length=200, null=True)),
                ('mission', models.TextField(null=True)),
                ('description', models.TextField(null=True)),
                ('govt_reg_number', models.CharField(max_length=200, null=True)),
                ('govt_reg_number_type', models.CharField(max_length=200, null=True)),
                ('registration_date_year', models.CharField(max_length=200, null=True)),
                ('registration_date_month', models.CharField(max_length=200, null=True)),
                ('registration_date_day', models.CharField(max_length=200, null=True)),
                ('gross_income', models.CharField(max_length=200, null=True)),
                ('image', models.TextField(max_length=200, null=True)),
                ('domain', models.CharField(max_length=200, null=True)),
                ('urls_scraped', models.TextField(null=True)),
            ],
        ),
    ]