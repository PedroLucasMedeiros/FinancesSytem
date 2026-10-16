"""Mixins reutilizáveis da API do dashboard.

Ficam isolados aqui para que serializers e views dependam deles, e não
um do outro. Cada mixin tem uma única responsabilidade.
"""
from rest_framework.permissions import IsAuthenticated

from dashboard.models import Person


# ---------------------------------------------------------------------------
# Mixins de serializer
# ---------------------------------------------------------------------------
class OwnedPersonSerializerMixin:
    """Restringe o campo `person` às pessoas do usuário autenticado.

    Sem isso, um usuário poderia criar registros na Person de outro
    enviando o UUID dela no payload.

    Uso: herdar ANTES de serializers.ModelSerializer.
    """

    person_field_name = "person"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        person_field = self.fields.get(self.person_field_name)
        if person_field is not None and request and request.user.is_authenticated:
            person_field.queryset = Person.objects.filter(user=request.user)


# ---------------------------------------------------------------------------
# Mixins de view
# ---------------------------------------------------------------------------
class LoginRequiredMixin:
    """Exige usuário autenticado (equivalente DRF do LoginRequiredMixin do Django).

    A forma de autenticar (JWT, sessão) vem do DEFAULT_AUTHENTICATION_CLASSES
    do settings, então este mixin não muda quando a autenticação mudar.
    """

    permission_classes = [IsAuthenticated]


class OwnerScopedQuerySetMixin:
    """Isola os dados: cada usuário enxerga apenas os seus registros.

    Defina `owner_lookup` com o caminho ORM até o usuário dono:
      - "person__user" (padrão): models ligadas a Person
      - "user": quando o model aponta direto para o usuário (ex.: Person)

    Uso: herdar ANTES de GenericViewSet, para que super().get_queryset()
    alcance o GenericAPIView.
    """

    owner_lookup = "person__user"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Geração do schema (Swagger): não há usuário real, retorna vazio
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        return queryset.filter(**{self.owner_lookup: self.request.user})


class AssignUserOnCreateMixin:
    """Preenche `user` com request.user na criação, ignorando o payload."""

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)