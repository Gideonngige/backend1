"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import dj_database_url
import os
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

#'django-insecure-warma_a=ah#lg$($qcbr_$f_80ij@42e&ph^u-5bv$&u@5q&!l'
# SECRET_KEY = os.environ.get('SECRET_KEY')
SECRET_KEY = 'django-insecure-warma_a=ah#lg$($qcbr_$f_80ij@42e&ph^u-5bv$&u@5q&!l'

# SECURITY WARNING: don't run with debug turned on in production!
# DEBUG = os.environ.get('DEBUG','False').lower() == 'True'
DEBUG = True

# ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS','').split(' ')

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'backend_app',
    'rest_framework',
    'django_daraja',
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_WHITELIST = (
'http://localhost:8081',
'http://localhost:8000',
)


ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# database_url = 'postgresql://chamavaultdb_user:6KK2CJmbOaQ4I0LD39D6qnqnzQu1QfSJ@dpg-cvau3idumphs73aj1qc0-a.oregon-postgres.render.com/chamavaultdb'
# DATABASES['default'] = dj_database_url.parse(database_url)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chamavaultdb',  # Ensure this is correct
        'USER': 'chamavaultdb_user',  # Remove extra spaces if any
        'PASSWORD': '6KK2CJmbOaQ4I0LD39D6qnqnzQu1QfSJ',  # Ensure it's correct
        'HOST': 'dpg-cvau3idumphs73aj1qc0-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}


# database_url = os.environ.get('DATABASE_URL')
# DATABASES['default'] = dj_database_url.parse(database_url)



# postgresql://chamavaultdb_user:6KK2CJmbOaQ4I0LD39D6qnqnzQu1QfSJ@dpg-cvau3idumphs73aj1qc0-a.oregon-postgres.render.com/chamavaultdb

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

#send email
#email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'ushindigideon01@gmail.com'
EMAIL_HOST_PASSWORD = 'rrst fhrj pojn agkt'


#daraja api
# The Mpesa environment to use
# Possible values: sandbox, production
MPESA_ENVIRONMENT = 'sandbox'
# Credentials for the daraja app
MPESA_CONSUMER_KEY = '17tijAWZQBWLRIFFuJrDGBfl1zalwr00g6wEE20cGdeHvw7l'
MPESA_CONSUMER_SECRET = 'iX29aYc7ujvLlXssKhvG2ilFzS7Bpoa5dU9SIGoPUDrdkLWwKQD1rUEOhW7BRQ3e'
#Shortcode to use for transactions. For sandbox use the Shortcode 1
#provided on test credentials page
MPESA_SHORTCODE = '1'
# Shortcode to use for Lipa na MPESA Online (MPESA Express) transactions
# This is only used on sandbox, do not set this variable in production
# For sandbox use the Lipa na MPESA Online Shorcode provided on test
#credentials page
MPESA_EXPRESS_SHORTCODE = '174379'
# Type of shortcode
# Possible values:
# - paybill (For Paybill)
# - till_number (For Buy Goods Till Number)
MPESA_SHORTCODE_TYPE = '174379'
# Lipa na MPESA Online passkey
# Sandbox passkey is available on test credentials page
# Production passkey is sent via email once you go live
MPESA_PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
# Username for initiator (to be used in B2C, B2B, AccountBalance and
#TransactionStatusQuery Transactions)
MPESA_INITIATOR_USERNAME = 'testapi'
# Plaintext password for initiator (to be used in B2C, B2B, AccountBalance
#and TransactionStatusQuery Transactions)
MPESA_INITIATOR_SECURITY_CREDENTIAL = 'Skb4kUuWtvsO//466Z4Jafbr3/9zZ8B7IxW4nutAPmOAcvEU4xFOVy0OaSVIJhXUFc+TIKatiXWnlkVWVefJK5kxLnq0FTQMzBGam8Yle4y/bNLj5b+jgieqpUZPfYceqktqPEjkH9K+XOhT7VIABCc/klFAXOvapx/yVesOkCgkVKbe4/vpBlA74zJ/9cH+KQyk32l+asLtgPr8qiYq3nT3HDVeYof6hQT/vQXUtd+RVHGuU8glfFj55cC2nv4/eQEKqkeHVgOardY8GXqW65vtNQSVqNec5ETLxsEqy+zbNoBZEt6uTtCNwxl2c9rcHUYKLHigVT+YUl4awnN5eQ=='
