from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Board
from ..users.models import User
from .serializers import BoardCreateSerializer
import datetime
from django.db.models import Q


class BoardsAPI(APIView):
    def get(self, request):
        # todo hashtag
        try:
            return Response({"result": "success"}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"msg": "서버에 에러가 발생했습니다."})

    def post(self, request):
        try:
            request_body = request.data
            # 필수 파라미터 체크
            if not request_body.keys() >= {"title", "content", "hashtag"}:
                return Response({"msg": "필수 입력 항목이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
            request_body["hashtag"] = request_body["hashtag"].replace("#", "")
            request_body["writer"] = request.user
            # 게시물 등록
            board = Board(
                title=request_body["title"],
                content=request_body["content"],
                hashtag=request_body["hashtag"],
                writer=request.user,
            )
            board.save()
            return Response({"msg": "게시글이 등록되었습니다."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response({"msg": "서버에 에러가 발생했습니다."})


class BoardAPI(APIView):
    def get(self, request, id):
        Response({"result": "ok"}, status=status.HTTP_200_OK)

    def put(self, request, id):
        Response({"result": "ok"}, status=status.HTTP_200_OK)

    def delete(self, request, id):
        Response({"result": "ok"}, status=status.HTTP_200_OK)
