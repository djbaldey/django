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
            options={'verbose_name': 'user', 'verbose_name_plural': 'users', 'permissions': (('add_superuser', 'Can add superuser'), ('change_superuser', 'Can change superuser'), ('delete_superuser', 'Can delete superuser'), ('add_staff', 'Can add staff'), ('change_staff', 'Can change staff'), ('delete_staff', 'Can delete staff'), ('add_active_user', 'Can add active user'), ('add_user_with_password', 'Can add user with password'), ('change_user_password', 'Can change the user password'), ('change_user_activity', 'Can change the user activity'), ('change_user_groups', 'Can change user groups'), ('change_user_perms', 'Can change user permissions'))},
        ),
        migrations.AddField(
            model_name='user',
            name='last_activity',
            field=models.DateTimeField(null=True, verbose_name='last activity', blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='settings',
            field=models.JSONField(verbose_name='settings', null=True, editable=False, blank=True),
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
