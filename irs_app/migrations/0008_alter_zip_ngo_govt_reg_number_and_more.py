# Generated by Django 4.1.5 on 2023-03-30 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('irs_app', '0007_zip_ngo_delete_linemarker'),
    ]

    operations = [
        migrations.AlterField(
            model_name='zip_ngo',
            name='govt_reg_number',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='zip_ngo',
            name='organization_name',
            field=models.CharField(max_length=200),
        ),
    ]