#!/usr/bin/env python
import os
import sys

# Set name directory of environ
ENV = '' # '.virtualenvs/django{{ docs_version }}'

def getenv():
    path = os.path.abspath(os.path.dirname(__file__))
    while path:
        env = os.path.join(path, ENV)
        found = os.path.exists(env)
        if path == '/' and not found:
            raise EnvironmentError('Path `%s` not found' % ENV)
        elif found:
            return env
        else:
            path = os.path.dirname(path)


if __name__ == "__main__":

    if ENV:
        env = getenv()
        python = 'python%s.%s' % sys.version_info[:2]
        packages = os.path.join(env, 'lib', python, 'site-packages')
        sys.path.insert(0, packages)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "{{ project_name }}.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
