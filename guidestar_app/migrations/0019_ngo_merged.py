# Generated by Django 4.1.5 on 2023-04-30 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guidestar_app', '0018_remove_ngo_locked_remove_ngo_resolved_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ngo',
            name='merged',
            field=models.BooleanField(default=False),
        ),
    ]