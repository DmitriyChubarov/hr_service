import logging
from typing import Any, Optional
from django.db import models
from django.conf import settings

logger: logging.Logger = logging.getLogger(__name__)

class Worker(models.Model):
    first_name = models.CharField('Имя', max_length=25)
    middle_name = models.CharField('Отчество',max_length=25, blank=True)
    last_name = models.CharField('Фамилия',max_length=25)
    email = models.EmailField('email',unique=True)
    position = models.CharField('Должность',max_length=50)
    is_active = models.BooleanField('Активен ли?',default=True)
    hired_date = models.DateField('Дата приёма на работу',auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        verbose_name='Создатель записи',
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="workers_created"
    )

    class Meta:
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["position"]),
        ]

    def save(self, *args: Any, **kwargs: Any) -> None:
        is_create: bool = self.pk is None
        super().save(*args, **kwargs)
        if is_create:
            user: Optional[Any] = getattr(self, 'created_by', None)
            created_by: str = user.username if user else 'system'
            logger.info(f"Worker created: id={self.id}, name={self.last_name} {self.first_name}, by={created_by}")

    def __str__(self):
        return f"{self.last_name} {self.first_name}"