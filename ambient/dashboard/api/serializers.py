from decimal import Decimal

from django.db.models import Sum
from rest_framework import serializers

from dashboard.models import FinancialGoal, FinancialTransaction, Person, PlannedBudget

from .mixins import OwnedPersonSerializerMixin  # ← agora vem do arquivo de mixins

# Metadados imutáveis, repetidos no Meta de cada serializer
READ_ONLY_METADATA = ("id", "created_at", "updated_at", "deleted_at")

# (PersonSerializer, PlannedBudgetSerializer, FinancialTransactionSerializer
#  e FinancialGoalSerializer continuam exatamente como estavam)
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "user", "name", "created_at", "updated_at", "deleted_at")
        # `user` é preenchido pela view com request.user, nunca pelo payload
        read_only_fields = ("user", *READ_ONLY_METADATA)

    def validate(self, attrs):
        request = self.context["request"]
        # all_objects: o OneToOne também conflita com perfis excluídos logicamente
        if self.instance is None and Person.all_objects.filter(user=request.user).exists():
            raise serializers.ValidationError("Este usuário já possui um perfil de pessoa.")
        return attrs


class PlannedBudgetSerializer(OwnedPersonSerializerMixin, serializers.ModelSerializer):
    # Valor em reais derivado da porcentagem (property do model)
    allocated_amount = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = PlannedBudget
        fields = (
            "id", "person", "budget_title", "granted_amount",
            "allocated_percentage", "allocated_amount",
            "created_at", "updated_at", "deleted_at",
        )
        read_only_fields = READ_ONLY_METADATA

    def validate_granted_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("O valor cedido não pode ser negativo.")
        return value

    def validate_allocated_percentage(self, value):
        if not Decimal("0") <= value <= Decimal("100"):
            raise serializers.ValidationError("A porcentagem deve estar entre 0 e 100.")
        return value

    def validate(self, attrs):
        # A soma das porcentagens de uma pessoa não pode passar de 100%
        person = attrs.get("person") or getattr(self.instance, "person", None)
        percentage = attrs.get("allocated_percentage", getattr(self.instance, "allocated_percentage", None))
        if person and percentage is not None:
            already_allocated = (
                PlannedBudget.objects.filter(person=person)
                .exclude(pk=getattr(self.instance, "pk", None))
                .aggregate(total=Sum("allocated_percentage"))["total"]
                or Decimal("0")
            )
            if already_allocated + percentage > 100:
                raise serializers.ValidationError(
                    {"allocated_percentage": f"A soma dos orçamentos ultrapassaria 100% (já alocado: {already_allocated}%)."}
                )
        return attrs


class FinancialTransactionSerializer(OwnedPersonSerializerMixin, serializers.ModelSerializer):
    # Rótulo legível do tipo (ex.: "Receita"), útil para o frontend
    transaction_type_display = serializers.CharField(source="get_transaction_type_display", read_only=True)

    class Meta:
        model = FinancialTransaction
        fields = (
            "id", "person", "transaction_title", "transaction_date",
            "transaction_type", "transaction_type_display", "transaction_amount",
            "created_at", "updated_at", "deleted_at",
        )
        read_only_fields = READ_ONLY_METADATA

    def validate_transaction_amount(self, value):
        # Sempre positivo: o sinal é dado por transaction_type
        if value <= 0:
            raise serializers.ValidationError("O valor do lançamento deve ser maior que zero.")
        return value


class FinancialGoalSerializer(OwnedPersonSerializerMixin, serializers.ModelSerializer):
    # Campos calculados (properties do model)
    progress_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_completed = serializers.BooleanField(read_only=True)

    class Meta:
        model = FinancialGoal
        fields = (
            "id", "person", "goal_title", "target_amount", "current_amount",
            "progress_percentage", "is_completed",
            "created_at", "updated_at", "deleted_at",
        )
        read_only_fields = READ_ONLY_METADATA

    def validate_target_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor objetivo deve ser maior que zero.")
        return value

    def validate_current_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("O valor atual não pode ser negativo.")
        return value