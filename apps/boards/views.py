from re import search
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import serializers
from .models import Board, Heart
from ..users.models import User
from .serializers import (
    BoardCreateSerializer,
    BoardListSerailizer,
    HeartSerializer,
    BoardHeartSerializer,
    BoardSoftDeleteSerializer,
)
from django.db.models import Q
from rest_framework.decorators import api_view


class BoardsAPI(APIView):
    def get(self, request):
        # 게시물 리스트 조회
        # todo hashtag
        # ordering 작성일, 좋아요 수, 조회 수 orderBy=
        # searching search= 제목에 포함된 게시글
        # filtering hashtags =
        # pagenation default 10
        query_params = request.query_params
        # add filter
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"msg": "서버에 에러가 발생했습니다."})

    def post(self, request):
        # 게시물 등록
        try:
            request_body = request.data
            # 필수 파라미터 체크
            if not request_body.keys() >= {"title", "content", "hashtag"}:
                return Response({"msg": "필수 입력 항목이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
            # 해시태그 가공 후 추가 ex) #test,#code - > test,code
            request_body["hashtag"] = request_body["hashtag"].replace("#", "")
            # 작성자 추가
            request_body["writer"] = request.user.id
            # 게시물 등록
            serializer = BoardCreateSerializer(data=request_body)
            if serializer.is_valid():
                serializer.save()
            return Response({"msg": "게시글이 등록되었습니다."}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BoardAPI(APIView):
    def get(self, request, id):
        # 게시물 상세 조회
        try:
            # 게시글 정보 취득
            board = Board.objects.all().get(index=id, is_active=True)
            # 게시글 조회수 증가
            board.views_count += 1
            board.save()
            serializer = BoardListSerailizer(board)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, id):
        # 게시물 수정
        try:
            request_body = request.data
            board = Board.objects.all().get(index=id, is_active=True)
            if board.writer == request.user:
                request_body["hashtag"] = request_body["hashtag"].replace("#", "")
                request_body["writer"] = request.user.id
                board_serializer = BoardCreateSerializer(board, request_body)
                if board_serializer.is_valid():
                    board_serializer.save()
                    return Response({"msg": "게시글이 수정되었습니다."}, status=status.HTTP_200_OK)
                else:
                    print(board_serializer.errors)
                    raise
            else:
                return Response({"msg": "게시글 수정 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, id):
        # 게시물 삭제(soft delete) -> is_active True -> False
        try:
            # 게시글 정보 취득
            board = Board.objects.all().get(index=id, is_active=True)
            if board.writer == request.user:

                serializer = BoardSoftDeleteSerializer(board, data={"is_active": False})
                if serializer.is_valid():
                    serializer.save()
            else:
                return Response({"msg": "게시글 삭제 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"msg": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, id):
        # 게시물 복구 -> is_active False -> True
        try:
            # 게시글 정보 취득
            board = Board.objects.all().get(index=id, is_active=False)
            if board.writer == request.user:
                serializer = BoardSoftDeleteSerializer(board, data={"is_active": True})
                if serializer.is_valid():
                    serializer.save()
            else:
                return Response({"msg": "게시글 복구 권한이 없습니다."}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"msg": "게시글이 복구되었습니다."}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(["patch"])
def give_heart(request, id):
    # todo: serializer 사용
    try:
        # board 데이터 취득
        boards = Board.objects.filter(index=id, is_active=True)
        if boards:
            board = boards[0]
            # 해당 게시물과 해당 유저의 좋아요 데이터를 취득
            heart = Heart.objects.filter(user=request.user.pk, board=board.index)
            # 데이터가 있는 경우 좋아요 삭제
            if heart:
                heart[0].delete()
                board_dict = {"heart_count": board.heart_count - 1}
                board_serializer = BoardHeartSerializer(board, board_dict)
                if board_serializer.is_valid():
                    board_serializer.save()
                return Response({"msg": "좋아요 취소"}, status=status.HTTP_200_OK)
            # 데이터가 없는 경우 좋아요 추가
            else:
                heart_dict = {"user": request.user.id, "board": board.index}
                heart_serializer = HeartSerializer(data=heart_dict)
                board_dict = {"heart_count": board.heart_count + 1}
                board_serializer = BoardHeartSerializer(board, board_dict)
                if heart_serializer.is_valid() and board_serializer.is_valid():
                    heart_serializer.save()
                    board_serializer.save()
                    return Response({"msg": "좋아요"}, status=status.HTTP_200_OK)
                else:
                    print(heart_serializer.errors)
                    print(board_serializer.errors)
                    raise
    except Exception as e:
        print(e)
        return Response({"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
