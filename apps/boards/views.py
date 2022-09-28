from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import Board, Heart, Hashtag
from .serializers import (
    BoardCreateSerializer,
    BoardListSerailizer,
    HeartSerializer,
    BoardHeartSerializer,
    BoardSoftDeleteSerializer,
)
from django.db.models import Q
from rest_framework.decorators import api_view
import json


class BoardsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # 게시물 리스트 조회
        # todo hashtag
        # ordering 작성일, 좋아요 수, 조회 수 orderBy=
        # searching search= 제목에 포함된 게시글
        # filtering hashtags =
        # pagenation default 10
        try:
            query_params = request.query_params
            if "page" not in query_params.keys():
                return Response({"msg": "page를 지정해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            q = Q()
            tag_list = []
            if "hashtags" in query_params:
                hashtag_list = query_params["hashtags"].split(",")
                flg = False
                tag_list = []
                for i in hashtag_list:
                    a = Hashtag.objects.filter(tag_content=i).first()
                    if a:
                        tag_list.append(a)
                    else:
                        flg = True
                        break
                if flg:
                    return Response({"board_list": []}, status=status.HTTP_200_OK)
                q.add(Q(tagging__in=tag_list), q.AND)
            # add filter
            q.add(Q(is_active=True), q.AND)
            if "search" in query_params:
                q.add(Q(title__contains=query_params["search"]), q.AND)
            # page 번호 체크
            page = int(request.query_params["page"])
            count = 10
            offset = int((count * (page - 1)))
            boards = Board.objects.filter(q)
            if tag_list:
                for i in tag_list:
                    boards = boards.filter(tagging__in=[i])
            if "orderBy" in query_params:
                boards = boards.distinct().order_by(query_params["orderBy"])[
                    offset : offset + count
                ]
            else:
                boards = boards.distinct().order_by("-created_at")[offset : offset + count]
            serializer = BoardListSerailizer(boards, many=True)
            return Response(
                json.dumps({"board_list": serializer.data}, ensure_ascii=False),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        # 게시물 등록
        try:
            request_body = request.data
            # 필수 파라미터 체크
            if not request_body.keys() >= {"title", "content", "hashtag"}:
                return Response({"msg": "필수 입력 항목이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
            request_body["writer"] = request.user.id
            request_body["tagging"] = []
            hashtag_list = request_body["hashtag"].split(",")
            for i in hashtag_list:
                if i[0] != "#":
                    return Response({"msg": "해시태그 형식이 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    tag = Hashtag.objects.filter(tag_content=i[1:]).first()
                    if tag == None:
                        tag = Hashtag()
                        tag.tag_content = i[1:]
                        tag.save()
                    request_body["tagging"].append(tag.pk)
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
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        # 게시물 상세 조회
        try:
            # 게시글 정보 취득
            board = Board.objects.all().get(index=id, is_active=True)
            # 게시글 조회수 증가
            board.views_count += 1
            board.save()
            tag_list = board.tagging.all()
            board.hashtag = tag_list
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
            board = Board.objects.get(index=id, is_active=True)
            if board.writer == request.user:
                # 필수 파라미터 체크
                if not request_body.keys() >= {"title", "content", "hashtag"}:
                    return Response({"msg": "필수 입력 항목이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
                request_body["tagging"] = []
                hashtag_list = request_body["hashtag"].split(",")
                for i in hashtag_list:
                    if i[0] != "#":
                        return Response(
                            {"msg": "해시태그 형식이 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        tag = Hashtag.objects.filter(tag_content=i[1:]).first()
                        if tag == None:
                            tag = Hashtag()
                            tag.tag_content = i[1:]
                            tag.save()
                        request_body["tagging"].append(tag.pk)
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
            board = Board.objects.get(index=id, is_active=True)
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
            board = Board.objects.get(index=id, is_active=False)
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
