# Generated by Django 4.1.5 on 2023-04-04 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('c_navigator', '0005_lastpage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ngo',
            options={'ordering': ['organization_name'], 'verbose_name_plural': 'NGOs'},
        ),
        migrations.AlterField(
            model_name='ngo',
            name='govt_reg_number',
            field=models.CharField(max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='ngo',
            name='organization_name',
            field=models.CharField(max_length=200),
        ),
    ]