from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view, inline_serializer
from rest_framework import mixins, serializers, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.models import User

from .serializers import LogoutSerializer, RegisterSerializer, UserSerializer

TAG = ["Autenticação"]


# --- Views do SimpleJWT, apenas para receberem tag e descrição no Swagger ---
@extend_schema(tags=TAG, summary="Login (e-mail e senha)",
               description="Retorna o par `access` + `refresh`.")
class DocumentedTokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=TAG, summary="Renovar access token",
               description="Com a rotação ativa, devolve também um novo `refresh`.")
class DocumentedTokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=TAG, summary="Verificar token",
               description="Responde 200 se o token for válido.")
class DocumentedTokenVerifyView(TokenVerifyView):
    pass


# --- Views do app ---
class StatusViewSet(viewsets.ViewSet):
    """Health check: sem model nem serializer, então não usa mixins."""
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=TAG, summary="Status da API",
        responses=inline_serializer("StatusResponse", {"status": serializers.CharField()}),
    )
    def retrieve(self, request):
        return Response({"status": "ok"})
    

@extend_schema_view(create=extend_schema(
    tags=TAG, summary="Cadastro de usuário",
    description="Cria o usuário e o perfil `Person` vinculado.",
))
class RegisterViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer
    queryset = User.objects.none()  # só cria; o queryset serve apenas ao schema


@extend_schema_view(retrieve=extend_schema(tags=TAG, summary="Usuário autenticado"))
class MeViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return super().get_queryset().none()
        return super().get_queryset().filter(pk=self.request.user.pk)

    def get_object(self):
        # A rota /me/ não tem {id}: o objeto é sempre o próprio usuário
        return self.get_queryset().get()


@extend_schema_view(create=extend_schema(
    tags=TAG, summary="Logout",
    description="Coloca o refresh token na blacklist.",
    responses={
        201: OpenApiResponse(description="Token invalidado."),
        400: OpenApiResponse(description="Token inválido ou expirado."),
    },
))
class LogoutViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = LogoutSerializer