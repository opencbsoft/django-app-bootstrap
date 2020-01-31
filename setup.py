import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

if os.getenv('CI_PIPELINE_IID'):
    version = '0.1.{}'.format(os.getenv('CI_PIPELINE_IID', ))
    with open(os.path.join(os.path.dirname(__file__), 'django_app_bootstrap/__init__.py'), 'w') as version_file:
        version_file.write('version="{}"'.format(version))
else:
    with open(os.path.join(os.path.dirname(__file__), 'django_app_bootstrap/__init__.py')) as version_file:
        version = version_file.read().split('=')[1].replace('"', '')

setup(
    name='django_app_bootstrap',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='GNU',
    description='Quickly generate application from django model files',
    long_description=README,
    url='https://www.bapp.ro/',
    author='Cristian Boboc',
    author_email='cristi@cbsoft.ro',
    install_requires=[],
)
