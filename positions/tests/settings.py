import os
SECRET_KEY = 'sekr3t'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'positions.tests.lists',
    'positions.tests.nodes',
    'positions.tests.generic',
    'positions.tests.todo',
    'positions.tests.store',
    'positions.tests.photos',
    'positions.tests.school',
    'positions.tests.restaurants',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
coverage_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'report')

NOSE_ARGS = [
    '--with-coverage',
    '--cover-package=positions',
    '--cover-html',
    '--cover-html-dir=%s' % coverage_dir,
    '--cover-inclusive',
]
