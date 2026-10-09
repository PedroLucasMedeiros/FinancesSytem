import uuid

from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class BaseModel(models.Model):
    """Modelo abstrato base: UUID, timestamps e soft delete."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)
    deleted_at = models.DateTimeField("excluído em", null=True, blank=True, db_index=True)

    # O primeiro manager declarado vira o _default_manager (usado pelo admin
    # e pelos related managers), então `objects` precisa vir primeiro.
    objects = SoftDeleteManager()
    all_objects = SoftDeleteManager(alive_only=False)

    class Meta:
        abstract = True

    @property
    def is_deleted(self):
        return self.deleted_at is not None

    def delete(self, using=None, keep_parents=False):
        """Soft delete: marca deleted_at em vez de remover a linha."""
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at", "updated_at"])
        return 1, {self._meta.label: 1}

    def hard_delete(self, using=None, keep_parents=False):
        """Exclusão física real (irreversível)."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        """Reativa um registro excluído logicamente."""
        self.deleted_at = None
        self.save(update_fields=["deleted_at", "updated_at"])