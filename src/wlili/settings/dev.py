from .base import *

INSTALLED_APPS += [
    "django_migrations_ci",
]


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-^x_0j4ms(v(0(&nyfb#mkctt4u^rtg)kdfhu)+z3^0b6893%2v"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = []

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Test database configuration for django-migrations-ci
DATABASES["default"]["TEST"] = {
    "NAME": BASE_DIR / "test_db.sqlite3",
}

# django-migrations-ci settings
MIGRATECI_PYTEST = True


try:
    from .local import *
except ImportError:
    pass
