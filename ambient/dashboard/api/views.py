from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from dashboard.models import FinancialGoal, FinancialTransaction, Person, PlannedBudget

from .docs import crud_docs
from .serializers import (
    FinancialGoalSerializer,
    FinancialTransactionSerializer,
    PersonSerializer,
    PlannedBudgetSerializer,
)


class CRUDViewSet(
    mixins.CreateModelMixin,     # POST      /recurso/
    mixins.RetrieveModelMixin,   # GET       /recurso/{id}/
    mixins.UpdateModelMixin,     # PUT/PATCH /recurso/{id}/
    mixins.DestroyModelMixin,    # DELETE    /recurso/{id}/ (chama instance.delete() = soft delete)
    mixins.ListModelMixin,       # GET       /recurso/
    viewsets.GenericViewSet,
):
    """Base: apenas as mixins nativas do DRF, sem métodos manuais."""


@crud_docs(tag="Pessoas", singular="pessoa", plural="pessoas")
class PersonViewSet(CRUDViewSet):
    """Gestão de pessoas: /api/dashboard/people/"""
    permission_classes = [IsAuthenticated]
    queryset = Person.objects.all()
    serializer_class = PersonSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):  # geração do schema: sem usuário real
            return super().get_queryset().none()
        return super().get_queryset().filter(user=self.request.user)


@crud_docs(tag="Orçamentos", singular="orçamento planejado", plural="orçamentos planejados")
class PlannedBudgetViewSet(CRUDViewSet):
    """Gestão de orçamentos planejados: /api/dashboard/budgets/"""
    permission_classes = [IsAuthenticated]
    queryset = PlannedBudget.objects.select_related("person")
    serializer_class = PlannedBudgetSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return super().get_queryset().none()
        return super().get_queryset().filter(person__user=self.request.user)


@crud_docs(tag="Lançamentos", singular="lançamento", plural="lançamentos")
class FinancialTransactionViewSet(CRUDViewSet):
    """Gestão de lançamentos (receitas e despesas): /api/dashboard/transactions/"""
    permission_classes = [IsAuthenticated]
    queryset = FinancialTransaction.objects.select_related("person")
    serializer_class = FinancialTransactionSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return super().get_queryset().none()
        return super().get_queryset().filter(person__user=self.request.user)


@crud_docs(tag="Metas", singular="meta financeira", plural="metas financeiras")
class FinancialGoalViewSet(CRUDViewSet):
    """Gestão de metas financeiras: /api/dashboard/goals/"""
    permission_classes = [IsAuthenticated]
    queryset = FinancialGoal.objects.select_related("person")
    serializer_class = FinancialGoalSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return super().get_queryset().none()
        return super().get_queryset().filter(person__user=self.request.user)