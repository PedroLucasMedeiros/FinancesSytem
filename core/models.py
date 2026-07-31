from django.db import models
from django.utils import timezone


# Mecanismo de consulta por filtros
class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def alive(self):
        return self.filter(deleted_at__isnull=True)

    def dead(self):
        return self.filter(deleted_at__isnull=False)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        # Utiliza o método .alive() do SoftDeleteQuerySet
        return SoftDeleteQuerySet(self.model, using=self._db).alive()


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Instância do gerenciador padrão e do alternativo
    objects = SoftDeleteManager()  # <-- Com parênteses!
    all_objects = models.Manager()

    class Meta:
        abstract = True

    # Métodos identados dentro do BaseModel:
    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(using=using)

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)