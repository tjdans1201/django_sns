from .models import User
from rest_framework import generics, status
from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate


# Create your views here.
class RegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    Response({"msg": "회원가입에 성공했습니다."}, status=status.HTTP_201_CREATED)


class LoginAPI(generics.GenericAPIView):
    """
    로그인 API
    누구나 접근 가능
    email, password, token으로 유효성 판단
    token을 리턴함
    """

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data["email"]
            password = request.data["password"]
            user = authenticate(email=email, password=password)
            if user is None:
                return Response({"message": "존재하지않는 email입니다."}, status=status.HTTP_400_BAD_REQUEST)
            if user is not None:
                token = TokenObtainPairSerializer.get_token(user)
                refresh_token = str(token)
                access_token = str(token.access_token)
                response = Response(
                    {
                        "msg": "로그인에 성공했습니다.",
                        "jwt_token": {
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
                response.set_cookie("access_token", access_token, httponly=True)
                response.set_cookie("refresh_token", refresh_token, httponly=True)
                return response
            else:  # 그 외
                return Response({"msg": "로그인에 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"msg": "서버에 에러가 발생했습니다."})
