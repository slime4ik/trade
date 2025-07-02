from django.apps import AppConfig
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

class AdConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ad'
    def ready(self):
        from .models import Category
        # Если есть изменения в Category очищаем кэш чтобы видеть актуальные категории
        @receiver([post_save, post_delete], sender=Category)
        def clear_category_cache(sender, **kwargs):
            cache.delete('all_categories')