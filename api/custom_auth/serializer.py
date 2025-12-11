from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import ModelSerializer


class CustomUserCreateSerializer(ModelSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ("role",)


class CustomUserSerializer(ModelSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields
