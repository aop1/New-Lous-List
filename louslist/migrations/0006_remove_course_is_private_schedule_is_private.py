# Generated by Django 4.1.1 on 2022-11-12 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('louslist', '0005_course_is_private'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='is_private',
        ),
        migrations.AddField(
            model_name='schedule',
            name='is_private',
            field=models.IntegerField(default=3),
        ),
    ]
