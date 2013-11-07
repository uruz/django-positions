import os
SECRET_KEY = 'sekr3t'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'positions.examples.lists',
    'positions.examples.nodes',
    'positions.examples.generic',
    'positions.examples.todo',
    'positions.examples.store',
    'positions.examples.photos',
    'positions.examples.school',
    'positions.examples.restaurants',
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
