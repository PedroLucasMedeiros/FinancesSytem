from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.validators import UniqueValidator

from dashboard.models import Person

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.all_objects.all())],
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "password")
        read_only_fields = ("id",)

    @transaction.atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        # Cada usuário nasce com sua Person, base do isolamento do dashboard
        Person.objects.create(user=user, name=f"{user.first_name} {user.last_name}".strip())
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "date_joined")
        read_only_fields = fields



class LogoutSerializer(serializers.Serializer):
    # write_only: o token não é devolvido na resposta
    refresh = serializers.CharField(write_only=True, help_text="Refresh token a ser invalidado.")

    def validate_refresh(self, value):
        try:
            token = RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError("Token inválido ou expirado.")
        # Um usuário só pode invalidar o próprio token
        if str(token["user_id"]) != str(self.context["request"].user.pk):
            raise serializers.ValidationError("Token inválido ou expirado.")
        self._token = token
        return value

    def create(self, validated_data):
        self._token.blacklist()  # chamado pelo CreateModelMixin via serializer.save()
        return validated_data