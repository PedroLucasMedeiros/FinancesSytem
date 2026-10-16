from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
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
    refresh = serializers.CharField(help_text="Refresh token a ser invalidado.")