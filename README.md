# DJANGO APP BOOTSTRAP

A simple django application that can speedup your development by generating code from models.

Specify a different application structure to process by entering the full path to the folder in settings.py variable BOOTSRAP_FOLDER

Quick start
-----------

1. pip install django-app-bootstrapp
2. Add "django_app_bootstrap" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_app_bootstrap',
    ]

3. Run `python manage.py bootstrap_app` to start the wizard.
