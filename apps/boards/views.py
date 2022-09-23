from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Board
from ..users.models import User
from .serializers import BoardCreateSerializer, BoardListSerailizer
import datetime
from django.db.models import Q


class BoardsAPI(APIView):
    def get(self, request):
        # todo hashtag
        # ordering 작성일, 좋아요 수, 조회 수 orderBy=
        # searching search= 제목에 포함된 게시글
        # filtering hashtags =
        # pagenation default 10
        query_params = request.query_params
        q = Q()
        q.add(Q(is_active=True), q.AND)
        if "search" in query_params:
            q.add(Q(content__contains=query_params["search"]), q.AND)
        if "hashtags" in query_params:
            hashtag_list = query_params["hashtags"].split(",")
            for i in hashtag_list:
                q.add(Q(hashtag__contains=i), q.AND)
        # page 번호 체크
        page = int(request.query_params["page"])
        count = 10
        offset = int((count * (page - 1)))
        if "orderBy" in query_params:
            boards = (
                Board.objects.all()
                .filter(q)
                .order_by(query_params["orderBy"])[offset : offset + count]
            )
        else:
            boards = Board.objects.all().filter(q).order_by("-created_at")[offset : offset + count]
            serializer = BoardListSerailizer(boards, many=True)

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
