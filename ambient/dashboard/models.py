from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from core.models import BaseModel

MIN_MONEY_VALUE = Decimal("0.00")
MIN_TRANSACTION_VALUE = Decimal("0.01")


class Person(BaseModel):
    name = models.CharField("nome completo", max_length=150)

    class Meta:
        verbose_name = "pessoa"
        verbose_name_plural = "pessoas"
        ordering = ["name"]

    def __str__(self):
        return self.name


class PlannedBudget(BaseModel):
    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="planned_budgets",
        verbose_name="pessoa",
    )
    budget_title = models.CharField("título do orçamento", max_length=100)
    granted_amount = models.DecimalField(
        "valor cedido",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(MIN_MONEY_VALUE)],
    )
    allocated_percentage = models.DecimalField(
        "porcentagem destinada (%)",
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(MIN_MONEY_VALUE), MaxValueValidator(Decimal("100"))],
    )

    class Meta:
        verbose_name = "orçamento planejado"
        verbose_name_plural = "orçamentos planejados"
        ordering = ["budget_title"]

    def __str__(self):
        return f"{self.budget_title} ({self.allocated_percentage}%)"

    @property
    def allocated_amount(self):
        """Valor em reais correspondente à porcentagem destinada."""
        return (self.granted_amount * self.allocated_percentage / Decimal("100")).quantize(Decimal("0.01"))


class FinancialTransaction(BaseModel):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Receita"
        EXPENSE = "EXPENSE", "Despesa"

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="pessoa",
    )
    transaction_title = models.CharField("descrição", max_length=150)
    transaction_date = models.DateField("data do lançamento")
    transaction_type = models.CharField(
        "tipo",
        max_length=7,
        choices=TransactionType.choices,
    )
    # Sempre positivo; o sinal é dado por transaction_type
    transaction_amount = models.DecimalField(
        "valor",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(MIN_TRANSACTION_VALUE)],
    )

    class Meta:
        verbose_name = "lançamento"
        verbose_name_plural = "lançamentos"
        ordering = ["-transaction_date", "-created_at"]
        indexes = [
            models.Index(fields=["person", "transaction_date"]),
            models.Index(fields=["person", "transaction_type", "transaction_date"]),
        ]

    def __str__(self):
        return f"{self.transaction_title} - {self.get_transaction_type_display()} R$ {self.transaction_amount}"


class FinancialGoal(BaseModel):
    goal_title = models.CharField("nome da meta", max_length=120)
    target_amount = models.DecimalField(
        "valor objetivo",
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(MIN_TRANSACTION_VALUE)],
    )
    current_amount = models.DecimalField(
        "valor atual",
        max_digits=12,
        decimal_places=2,
        default=MIN_MONEY_VALUE,
        validators=[MinValueValidator(MIN_MONEY_VALUE)],
    )

    class Meta:
        verbose_name = "meta financeira"
        verbose_name_plural = "metas financeiras"
        ordering = ["goal_title"]

    def __str__(self):
        return self.goal_title

    @property
    def progress_percentage(self):
        if not self.target_amount:
            return Decimal("0.00")
        progress = self.current_amount / self.target_amount * Decimal("100")
        return min(Decimal("100"), progress).quantize(Decimal("0.01"))

    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount