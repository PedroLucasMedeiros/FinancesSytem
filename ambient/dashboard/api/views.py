from rest_framework import mixins, viewsets

from dashboard.models import FinancialGoal, FinancialTransaction, Person, PlannedBudget

from .mixins import AssignUserOnCreateMixin, LoginRequiredMixin, OwnerScopedQuerySetMixin
from .serializers import (
    FinancialGoalSerializer,
    FinancialTransactionSerializer,
    PersonSerializer,
    PlannedBudgetSerializer,
)


class OwnedResourceViewSet(
    LoginRequiredMixin,          # exige autenticação
    OwnerScopedQuerySetMixin,    # filtra pelos dados do usuário logado
    mixins.CreateModelMixin,     # POST      /recurso/
    mixins.ListModelMixin,       # GET       /recurso/
    mixins.RetrieveModelMixin,   # GET       /recurso/{id}/
    mixins.UpdateModelMixin,     # PUT/PATCH /recurso/{id}/
    mixins.DestroyModelMixin,    # DELETE    /recurso/{id}/ (soft delete)
    viewsets.GenericViewSet,
):
    """Base: CRUD completo, restrito ao usuário logado.

    DestroyModelMixin.perform_destroy chama instance.delete(), que no
    BaseModel é o soft delete (preenche deleted_at). Nada é apagado do banco.
    """


class PersonViewSet(AssignUserOnCreateMixin, OwnedResourceViewSet):
    """Gestão de pessoas: /api/dashboard/people/"""
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    owner_lookup = "user"  # Person aponta direto para o usuário


class PlannedBudgetViewSet(OwnedResourceViewSet):
    """Gestão de orçamentos planejados: /api/dashboard/budgets/"""
    queryset = PlannedBudget.objects.select_related("person")
    serializer_class = PlannedBudgetSerializer


class FinancialTransactionViewSet(OwnedResourceViewSet):
    """Gestão de lançamentos (receitas e despesas): /api/dashboard/transactions/"""
    queryset = FinancialTransaction.objects.select_related("person")
    serializer_class = FinancialTransactionSerializer


class FinancialGoalViewSet(OwnedResourceViewSet):
    """Gestão de metas financeiras: /api/dashboard/goals/"""
    queryset = FinancialGoal.objects.select_related("person")
    serializer_class = FinancialGoalSerializer