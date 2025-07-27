from django.apps import AppConfig


class StockgardenConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'StockGarden'

        
    def ready(self):
        try:
            import StockGarden.signals 
        except ImportError as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error importing signals: {str(e)}")