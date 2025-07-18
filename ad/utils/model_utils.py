from django.core.cache import cache
from ad.models import Category

def get_categories():
    """
    Кеш на 15 чтобы каждый раз не искать
    обращаться к бд при рендере формочки
    """
    return cache.get_or_set('all_categories', lambda: Category.objects.all(), 60*15)
