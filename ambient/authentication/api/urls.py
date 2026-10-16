from core.routers import SingletonRouter

from .views import LogoutViewSet, MeViewSet, RegisterViewSet, StatusViewSet

app_name = "authentication"

router = SingletonRouter()
router.register("status", StatusViewSet, basename="status")
router.register("register", RegisterViewSet, basename="register")
router.register("me", MeViewSet, basename="me")
router.register("logout", LogoutViewSet, basename="logout")

urlpatterns = router.urls