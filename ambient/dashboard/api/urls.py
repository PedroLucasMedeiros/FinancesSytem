from rest_framework.routers import DefaultRouter

from .views import (
    FinancialGoalViewSet,
    FinancialTransactionViewSet,
    PersonViewSet,
    PlannedBudgetViewSet,
)

app_name = "dashboard"

router = DefaultRouter()
router.register("people", PersonViewSet, basename="person")
router.register("budgets", PlannedBudgetViewSet, basename="budget")
router.register("transactions", FinancialTransactionViewSet, basename="transaction")
router.register("goals", FinancialGoalViewSet, basename="goal")

urlpatterns = router.urls