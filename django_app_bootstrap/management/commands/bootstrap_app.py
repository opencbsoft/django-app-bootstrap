import os
from django.apps import apps
from django.template import Context, Template

from django.core.management.base import BaseCommand
from django.conf import settings


def query_yes_no(console, question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        console.stdout.write(console.style.HTTP_INFO(question + prompt), ending='')
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            console.stdout.write(console.style.WARNING("Please respond with 'yes' or 'no' ""(or 'y' or 'n').\n"))


def process_template(console, app_name, context, bootstrap_folder, path):
    process = True
    source_file = path.replace(bootstrap_folder, '')
    dest_dir = os.path.join(settings.BASE_DIR, app_name)
    dest_file = source_file[1:].replace('.html', '.py')
    console.stdout.write(('Processing {} ...'.format(dest_file)))
    os.makedirs(os.path.dirname(os.path.join(dest_dir, dest_file)), exist_ok=True)

    if os.path.exists(os.path.join(dest_dir, dest_file)):
        if not query_yes_no(console, '{} exists, do you want to overwrite?'.format(dest_file), default='no'):
            process = False
    if process:
        context = Context(context)
        with open(path) as f:
            file_content = f.read()
        final_content = Template(str(file_content)).render(context)
        with open(os.path.join(dest_dir, dest_file), 'w+') as f:
            f.write(final_content)


class Command(BaseCommand):
    help = 'Bootstrap file structure for a selected application'

    def handle(self, *args, **options):
        local_apps = []
        external_apps = []
        for item in os.listdir(settings.BASE_DIR):
            for app in settings.INSTALLED_APPS:
                if '.' in app:
                    app = app.split('.')[0]
                if item == app:
                    local_apps.append(item)
        for app in settings.INSTALLED_APPS:
            if '.' in app :
                app = app.split('.')[0]
            if app not in local_apps and 'django' not in app:
                external_apps.append(app)
        self.stdout.write(self.style.HTTP_INFO(('Which application do you want to bootstrap?')))
        idx = 1
        for app in local_apps:
            print('{}.{}'.format(idx, app))
            idx += 1
        result = int(input('Select application (1-{}):'.format(idx-1))) - 1
        context = {}
        context['apps'] = {}
        context['local_apps'] = local_apps
        for app in local_apps + external_apps:
            app_config = apps.get_app_config(app)
            context['apps'][app] = dict()
            context['apps'][app]['name'] = app
            context['apps'][app]['models'] = []
            for app_name, model in app_config.models.items():
                if not model._meta.auto_created:
                    full_model = {}
                    full_model['name'] = model.__name__
                    full_model['fields'] = []
                    for field in model._meta.get_fields():
                        field_name = str(field).split('.')[-1].replace('>', '')
                        if 'Many' not in str(field):
                            if field.remote_field:
                                field_name += ':' + str(field.remote_field.model).replace('>', '').replace("'", "").replace('<class', '').strip()
                            full_model['fields'].append(field_name)
                    context['apps'][app]['models'].append(full_model)
            if len(context['apps'][app]['models']) == 0:
                del context['apps'][app]
        context['selected_app'] = local_apps[result]
        context['models'] = []
        for app_name, model in apps.get_app_config(context['selected_app']).models.items():
            if not model._meta.auto_created:
                full_model = {}
                full_model['name'] = model.__name__
                full_model['fields'] = []
                for field in model._meta.get_fields():
                    field_name = str(field).split('.')[-1].replace('>', '')
                    if 'Many' not in str(field):
                        full_model['fields'].append(field_name)
                context['models'].append(full_model)
        bootstrap_folder = getattr(settings, 'BOOTSRAP_FOLDER', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bootstrap_files'))
        for item in os.listdir(bootstrap_folder):
            if os.path.isdir(os.path.join(bootstrap_folder, item)):
                subdir = os.path.join(bootstrap_folder, item)
                for file in os.listdir(subdir):
                    process_template(self, context['selected_app'], context, bootstrap_folder, os.path.join(subdir, file))
            else:
                process_template(self, context['selected_app'], context, bootstrap_folder, os.path.join(bootstrap_folder, item))
        # #print(bootstrap_files)
        self.stdout.write(self.style.SUCCESS(f'Finished bootstrapping app structure'))
