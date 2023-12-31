"""
Django settings for coinsAPI project.

Generated by 'django-admin startproject' using Django 4.2.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-dw)(y08pt^!*8951qe3b&7ppvc#ympbfwmj-u&_ndt-p^1mcx7"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

#### BITRANSFER SETTINGS ####

TESTNET = True
"""
Setting not necessary at the moment, created only for the addition of coins in the future,
in case of bitcoin it is necessary to specify the "--testnet" flag in the "bitcoind" command
example: "bitcoind --testnet etc..."
"""

MAX_REGISTRATION_ATTEMPTS = 5
REGISTRATION_TIMEOUT_SECONDS = 60 * 60

PAYMENTS_TIME_RANGE = timedelta(hours=3) # Time range in which created payments are checked
BTC_RPC_USER = "YourUsername" # Bitcoin Core rpc user, WARNING! CHANGE THIS
BTC_RPC_PSW = "YourSuperSecurePSWD" # Bitcoin core rpc password, WARNING! CHANGE THIS
BTC_WALLET_NAME = "wallet" # Bitcoin Core wallet name
MIN_BTC_CONFIRMATIONS = 3
MINIMUM_PAYMENT_IN_USD = 1 # WARNING! Do not set a lower value for the cost of two transactions, i suggest > 20, never set < 10
MAXIMUM_PAYMENT_IN_USD = 1000000 # I suggest to never change this to lower value
MINIMUM_WHITDRAW_IN_USD = 10

USER_PLANS_LIST = [
    {
        "id": 0, # For each plan increase this by 1
        "name": "Free plan", # Name of plan
        "dectiption_and_features": "A free plans with all features and 50 requests at minute",
        "price": 0, # amount in USD
        "rate": 1, # How much requests for "rate_unit"
        "rate_unit": "h", # "s" for seconds, "m" for minutes, "h" for hours, "d" for day
        "plan_duration": 525600 # Plan duration in minutes
    },
    {
        "id": 1, # For each plan increase this by 1
        "name": "Premium plan", # Name of plan
        "dectiption_and_features": "Premium plan with 100 request/hour",
        "price": 3, # amount in USD
        "rate": 100, # How much requests for "rate_unit"
        "rate_unit": "h", # "s" for seconds, "m" for minutes, "h" for hours, "d" for day
        "plan_duration": 525600 # Plan duration in minutes
    },
]



# List of coins, do not change nothing at the moment
COINS_LIST = [

    {
        "name": "bitcoin",
    }
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:4200",  # Angular app
    "http://localhost:4200",  # Angular app
]

#############################














































AUTH_USER_MODEL = 'coins.CustomUser'

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "coins",
    "axes",
    'rest_framework',
    'rest_framework.authtoken',

    'corsheaders',
    

]



MIDDLEWARE = [

    'django_ratelimit.middleware.RatelimitMiddleware',
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "axes.middleware.AxesMiddleware",
    "coins.middleware.StartupMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = "coinsAPI.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "coinsAPI.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend'
]

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

AXES_FAILURE_LIMIT = 10