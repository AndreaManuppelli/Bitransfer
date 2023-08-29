from django.apps import AppConfig
from django.db.backends.signals import connection_created

class BtcConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "coins"

    