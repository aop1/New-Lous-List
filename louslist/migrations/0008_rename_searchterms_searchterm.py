# Generated by Django 4.1.1 on 2022-11-16 00:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('louslist', '0007_alter_user_profile_pic_searchterms'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='SearchTerms',
            new_name='SearchTerm',
        ),
    ]
