# Generated by Django 4.1.1 on 2022-11-12 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('louslist', '0004_alter_user_profile_pic'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='is_private',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
    ]
