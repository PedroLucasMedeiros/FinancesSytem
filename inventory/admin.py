from django.contrib import admin
from .models import Category, Product, Sale


# 1. (Opcional) Criando um filtro para alternar na barra lateral direita
class DeletedStatusFilter(admin.SimpleListFilter):
    title = 'status de exclusão'
    parameter_name = 'deleted_status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Ativos'),
            ('deleted', 'Excluídos (Soft Delete)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'active':
            return queryset.filter(deleted_at__isnull=True)
        if self.value() == 'deleted':
            return queryset.filter(deleted_at__isnull=False)
        return queryset


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at", "deleted_at")
    list_filter = (DeletedStatusFilter,)

    # Força o Admin a usar o all_objects para trazer TUDO (inclusive excluídos)
    def get_queryset(self, request):
        return Category.all_objects.all()


@admin.register(Product)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "category", "created_at", "updated_at", "deleted_at")
    list_filter = (DeletedStatusFilter, "category")

    # Força o Admin a usar o all_objects para trazer TUDO (inclusive excluídos)
    def get_queryset(self, request):
        return Product.all_objects.all()


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "price_unity_retail", "created_at", "deleted_at")
    list_filter = (DeletedStatusFilter,)

    def get_queryset(self, request):
        return Sale.all_objects.all()