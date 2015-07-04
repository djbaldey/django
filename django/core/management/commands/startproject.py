from importlib import import_module
import locale

from django.core.management.base import CommandError
from django.core.management.templates import TemplateCommand
from django.utils.crypto import get_random_string

def parse_locale(loc):
    L = ('af', 'ar', 'ast', 'az', 'bg', 'be', 'bn', 'br', 'bs',
    'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'en-au', 'en-gb', 'eo',
    'es', 'es-ar', 'es-mx', 'es-ni', 'es-ve', 'et', 'eu', 'fa', 'fi',
    'fr', 'fy', 'ga', 'gl', 'he', 'hi', 'hr', 'hu', 'ia', 'id', 'io',
    'is', 'it', 'ja', 'ka', 'kk', 'km', 'kn', 'ko', 'lb', 'lt', 'lv',
    'mk', 'ml', 'mn', 'mr', 'my', 'nb', 'ne', 'nl', 'nn', 'os', 'pa',
    'pl', 'pt', 'pt-br', 'ro', 'ru', 'sk', 'sl', 'sq', 'sr', 'sr-latn',
    'sv', 'sw', 'ta', 'te', 'th', 'tr', 'tt', 'udm', 'uk', 'ur', 'vi',
    'zh-cn', 'zh-hans', 'zh-hant', 'zh-tw')

    loc = loc.lower().replace('_', '-')
    if loc in L:
        return loc
    loc = loc.split('-')[0]
    if loc in L:
        return loc
    return None


class Command(TemplateCommand):
    help = ("Creates a Django project directory structure for the given "
            "project name in the current directory or optionally in the "
            "given directory.")
    missing_args_message = "You must provide a project name."

    def handle(self, **options):
        project_name, target = options.pop('name'), options.pop('directory')
        self.validate_name(project_name, "project")

        # Check that the project_name cannot be imported.
        try:
            import_module(project_name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an existing "
                               "Python module and cannot be used as a "
                               "project name. Please try another name." %
                               project_name)

        # Create a random SECRET_KEY to put it in the main settings.
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        options['secret_key'] = get_random_string(50, chars)

        locale.setlocale(locale.LC_ALL, '')
        options['locale'] = parse_locale(locale.getlocale()[0])

        super(Command, self).handle('project', project_name, target, **options)
