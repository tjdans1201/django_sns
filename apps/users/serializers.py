# from django.contrib.auth.models import User
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "password2", "nickname")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            nickname=validated_data["nickname"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    """
    로그인
    로그인과 함께 토큰 생성
    """

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password", None)
        user = authenticate(email=email, password=password)

        if user:
            token = Token.objects.get(user=user)
            return token

        raise serializers.ValidationError({"error": "로그인 할 수 없습니다"})


# from rest_framework.
