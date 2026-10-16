from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from authentication.api.views import (
    DocumentedTokenObtainPairView,
    DocumentedTokenRefreshView,
    DocumentedTokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # --- JWT: obtenção e renovação de tokens (login por e-mail) ---
    path("api/token/", DocumentedTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", DocumentedTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", DocumentedTokenVerifyView.as_view(), name="token_verify"),

    # --- Apps ---
    path("api/auth/", include("authentication.api.urls")),   # cadastro, perfil, logout
    path("api/dashboard/", include("dashboard.api.urls")),   # domínio financeiro

    # --- Documentação (Swagger / OpenAPI) ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]