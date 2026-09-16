from django.apps import AppConfig
from django.contrib.auth.signals import user_logged_in

class LoginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.login"

    def ready(self):
        # Importar aquí, no arriba
        from django.contrib.auth.models import update_last_login
        user_logged_in.disconnect(update_last_login)
