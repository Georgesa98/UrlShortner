from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.serializers import ModelSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomUserCreateSerializer(ModelSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ("role",)


class CustomUserSerializer(ModelSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def get_token(self, user):
        token = super().get_token(user)
        token["role"] = user.role
        return token
