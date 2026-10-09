from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet com suporte a exclusão lógica (soft delete)."""

    def alive(self):
        """Somente registros ativos."""
        return self.filter(deleted_at__isnull=True)

    def deleted(self):
        """Somente registros excluídos logicamente."""
        return self.filter(deleted_at__isnull=False)

    def delete(self):
        """Soft delete em lote: preenche deleted_at em vez de apagar do banco.

        update() não dispara auto_now, então updated_at é preenchido manualmente.
        Retorna o mesmo formato do delete() padrão do Django.
        """
        now = timezone.now()
        affected_rows = self.alive().update(deleted_at=now, updated_at=now)
        return affected_rows, {self.model._meta.label: affected_rows}

    def hard_delete(self):
        """Exclusão física real (irreversível)."""
        return super().delete()

    def restore(self):
        """Reativa em lote os registros excluídos logicamente."""
        return self.deleted().update(deleted_at=None, updated_at=timezone.now())

    # Impede que o Manager exponha esses métodos (ex.: Model.objects.delete()
    # apagaria a tabela inteira). Eles só existem a partir de um QuerySet.
    delete.queryset_only = True
    hard_delete.queryset_only = True


class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
    """Manager que, por padrão, devolve apenas registros ativos.

    Uso no modelo:
        objects = SoftDeleteManager()                    # só ativos
        all_objects = SoftDeleteManager(alive_only=False)  # histórico completo
    """

    def __init__(self, *args, alive_only=True, **kwargs):
        self.alive_only = alive_only
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.alive() if self.alive_only else queryset