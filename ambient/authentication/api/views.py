from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import generics, serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

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
class StatusView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    @extend_schema(
        tags=TAG, summary="Status da API",
        responses=inline_serializer("StatusResponse", {"status": serializers.CharField()}),
    )
    def get(self, request):
        return Response({"status": "ok"})


@extend_schema(tags=TAG, summary="Cadastro de usuário",
               description="Cria o usuário e o perfil `Person` vinculado.")
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=TAG, summary="Usuário autenticado", responses=UserSerializer)
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=TAG, summary="Logout",
        description="Coloca o refresh token na blacklist.",
        request=LogoutSerializer,
        responses={
            205: OpenApiResponse(description="Token invalidado."),
            400: OpenApiResponse(description="Token ausente, inválido ou expirado."),
        },
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except TokenError:
            return Response({"detail": "Token inválido ou expirado."},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_205_RESET_CONTENT)