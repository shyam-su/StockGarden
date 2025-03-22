from django.apps import AppConfig


class StockgardenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'StockGarden'

    def ready(self):
        import StockGarden.signals 