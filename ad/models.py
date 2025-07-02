from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid
from django.contrib.postgres.indexes import GinIndex

# ============ Функции используемые в моделях ===============
def generate_article():
    return uuid.uuid4().hex[:8]
# ============ Функции используемые в моделях ===============


# Кастомизация стандартной модели пользователя в будущем
class User(AbstractUser):
    pass

# для наследования с полями user и created_at
class BaseCreate(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE) # можно creator/owner
    class Meta:
        abstract = True

class Category(models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name

class Ad(BaseCreate):
    CONDITION_CHOICES = [
        ('new', 'Новое'),
        ('used', 'Б/у'),
    ]
    article = models.CharField(
        primary_key=True, # pk сам индексируется
        max_length=8,
        unique=True,
        default=generate_article,  # Пример: 'a1b2c3d4' full random
        editable=False
    )
    condition = models.CharField(max_length=50,
                                 choices=CONDITION_CHOICES)
    title = models.CharField(max_length=40)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category,
                                 on_delete=models.CASCADE,   # у 1 объявления может быть 1 категория
                                 related_name='ads')  

    class Meta:
        indexes=[
            models.Index(fields=['category']),
            models.Index(fields=['user']),
            GinIndex(fields=['title', 'description'], name='search_gin_idx') # Только для PostgreSQL если SQlite - убрать
        ]
        ordering = ['-created_at']


    def __str__(self) -> str:
        return self.title

class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'На рассмотрении'),
        ('accepted', 'Принято'),
        ('rejected', 'Отклонено'),
    ]
    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name="Предлагаемый товар (отправитель)"
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name="Запрашиваемый товар (получатель)"
    )
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Предложение #{self.id}: {self.ad_sender.title} → {self.ad_receiver.title}"

    class Meta:
        unique_together = ('ad_sender', 'ad_receiver')
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]