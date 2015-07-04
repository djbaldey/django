# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.core.validators import RegexValidator


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'user', 'verbose_name_plural': 'users', 'permissions': (('create_user_password', 'Can create user with password'), ('update_user_password', 'Can update users password'), ('create_user_active', 'Can create active user'), ('update_user_active', 'Can update activity user'), ('create_user_superuser', 'Can create user as superuser'), ('update_user_superuser', 'Can update user as superuser'), ('create_user_staff', 'Can create user as staff'), ('update_user_staff', 'Can update user as staff'), ('update_user_groups', 'Can update user groups'), ('update_user_perms', 'Can update user permissions'))},
        ),
        migrations.AddField(
            model_name='user',
            name='last_activity',
            field=models.DateTimeField(null=True, verbose_name='last activity', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='settings',
            field=models.JSONField(null=True, verbose_name='settings', blank=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='content_type',
            field=models.ForeignKey(verbose_name='content type', to='contenttypes.ContentType'),
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, max_length=30, validators=[RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.', 'invalid', flags=32)], help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, verbose_name='username'),
        ),
    ]
