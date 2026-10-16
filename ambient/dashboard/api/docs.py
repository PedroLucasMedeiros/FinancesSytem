"""Decorators de documentação OpenAPI (Swagger) das ViewSets do dashboard."""
from drf_spectacular.utils import extend_schema, extend_schema_view


def crud_docs(*, tag: str, singular: str, plural: str):
    """Gera a documentação das 6 ações do CRUD de um recurso.

    Uso:
        @crud_docs(tag="Metas", singular="meta", plural="metas")
        class FinancialGoalViewSet(...): ...
    """
    return extend_schema_view(
        list=extend_schema(
            tags=[tag],
            summary=f"Listar {plural}",
            description=f"Retorna, de forma paginada, apenas as {plural} do usuário autenticado.",
        ),
        create=extend_schema(
            tags=[tag],
            summary=f"Criar {singular}",
            description=f"Cria uma nova {singular} vinculada ao usuário autenticado.",
        ),
        retrieve=extend_schema(
            tags=[tag],
            summary=f"Detalhar {singular}",
            description=f"Retorna uma {singular} pelo UUID. Registros de outros usuários respondem 404.",
        ),
        update=extend_schema(
            tags=[tag],
            summary=f"Substituir {singular}",
            description=f"Atualização completa (PUT): todos os campos obrigatórios devem ser enviados.",
        ),
        partial_update=extend_schema(
            tags=[tag],
            summary=f"Atualizar {singular} parcialmente",
            description="Atualização parcial (PATCH): envie apenas os campos que mudam.",
        ),
        destroy=extend_schema(
            tags=[tag],
            summary=f"Excluir {singular} (soft delete)",
            description=(
                "Exclusão lógica: o registro recebe `deleted_at` e deixa de aparecer na API, "
                "mas permanece no banco de dados."
            ),
            responses={204: None},
        ),
    )