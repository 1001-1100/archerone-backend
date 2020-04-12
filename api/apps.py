from django.apps import AppConfig

class ApiConfig(AppConfig):
    name = 'api'
    verbose_name = 'api'
    def ready(self):
        import os
        if os.environ.get('RUN_MAIN'):
            pass
