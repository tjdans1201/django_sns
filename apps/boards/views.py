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
        """
        게시글 리스트 조회
        1page당 10개씩 출력
        query_params의 orderBy에 따라 정렬(기본적으로 작성일 기준)
        query_params에 hashtag 또는 search가 있으면 검색 필터를 추가
        """
        try:
            query_params = request.query_params
            if "page" not in query_params.keys():
                return Response({"msg": "page를 지정해주세요."}, status=status.HTTP_400_BAD_REQUEST)
            # 검색 필터 선언
            q = Q()
            tag_list = []
            # 해시태그가 있는 경우
            if "hashtags" in query_params:
                # 주어진 해시태그를 ","로 구분
                hashtag_list = query_params["hashtags"].split(",")
                flg = False
                tag_list = []
                # 해시태그의 수 만큼 반복
                for i in hashtag_list:
                    # 해시태그 테이블에서 해당 태그를 조회
                    tag = Hashtag.objects.filter(tag_content=i).first()
                    if tag:
                        # 태그가 있으면 해당 객체를 태그 리스트에 추가
                        tag_list.append(tag)
                    else:
                        # 태그가 없으면 전체 게시물에 해당 해시태그가 없다는 뜻으로 flg를 True로 설정하고 비어있는 리스트를 리턴
                        flg = True
                        break
                if flg:
                    return Response({"board_list": []}, status=status.HTTP_200_OK)
            # 활성화된 게시글만 조회(게시글 삭제 시 is_active=False)
            q.add(Q(is_active=True), q.AND)
            # 검색 키워드가 있는 경우 제목에 해당 키워드가 포함된 게시글만 조회
            if "search" in query_params:
                q.add(Q(title__contains=query_params["search"]), q.AND)
            # page 번호 체크하고 개수 지정
            page = int(request.query_params["page"])
            count = 10
            offset = int((count * (page - 1)))
            # 추가된 필터로 게시글 조회
            boards = Board.objects.filter(q)
            # 검색 필터에 태그 리스트를 추가 : 리스트의 모든 해시태그가 포함된 게시글만 조회
            # Hashtag는 chain filter방식으로 추가
            if tag_list:
                for i in tag_list:
                    boards = boards.filter(tagging__in=[i])
            # 지정된 정렬 조건에 따라 게시글 조회
            if "orderBy" in query_params:
                boards = boards.distinct().order_by(query_params["orderBy"])[
                    offset : offset + count
                ]
            else:
                boards = boards.distinct().order_by("-created_at")[offset : offset + count]
            serializer = BoardListSerailizer(boards, many=True)
            return Response(
                {"board_list": serializer.data},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            print(e)
            return Response(
                {"msg": "서버에 에러가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """
        게시글 등록
        제목, 내용, 해시태그는 필수
        해시태그는 ","으로 구분하여 manytomany필드에 저장
        """
        # 게시물 등록
        try:
            request_body = request.data
            # 필수 파라미터 체크
            if not request_body.keys() >= {"title", "content", "hashtag"}:
                return Response({"msg": "필수 입력 항목이 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
            request_body["writer"] = request.user.id
            request_body["tagging"] = []
            # 해시태그는 ","로 구분
            hashtag_list = request_body["hashtag"].split(",")
            for i in hashtag_list:
                # 해시태그가 '#'으로 시작하지않으면 리퀘스트 에러
                if i[0] != "#":
                    return Response({"msg": "해시태그 형식이 틀렸습니다."}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # 해시태그 테이블에서 해당 태그를 조회
                    tag = Hashtag.objects.filter(tag_content=i[1:]).first()
                    # 태그가 없으면 해시태그 테이블에 추가
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
        """
        게시글 상세 조회
        게시글 조회 시 유저 관계 없이 조회수가 증가
        """

        try:
            # 게시글 정보 취득
            board = Board.objects.all().get(index=id, is_active=True)
            # 게시글 조회수 증가
            board.views_count += 1
            board.save()
            # 해당 게시글의 해시태그를 조회
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
        """
        게시글 수정
        작성자만 게시글의 수정 가능
        """
        try:
            request_body = request.data
            board = Board.objects.get(index=id, is_active=True)
            # 게시글의 작성자와 유저를 비교
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
        """
        게시글 삭제
        게시글은 작성자만 삭제가 가능
        soft_delete 방식으로 레코드의 삭제가 아닌 is_active 필드를 True -> False로 변경
        """
        try:
            # 게시글 정보 취득
            board = Board.objects.get(index=id, is_active=True)
            # 게시글의 작성자와 유저를 비교
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
        """
        게시글 복구
        게시글은 작성자만 복구가 가능
        is_active 필드를 False -> True로 변경하여 복구
        """
        try:
            # 게시글 정보 취득
            board = Board.objects.get(index=id, is_active=False)
            # 게시글의 작성자와 유저를 비교
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
    """
    게시글에 좋아요/좋아요 취소
    유저 관계없이 좋아요 가능
    1인당 한 게시물에 좋아요는 한번만 가능
    한번 더 좋아요를 누르는 경우 좋아요가 취소
    해당 게시글에 대한 유저의 좋아요 여부는 heart 테이블에 저장하여 체크
    """
    try:
        # board 데이터 취득
        boards = Board.objects.filter(index=id, is_active=True)
        if boards:
            board = boards[0]
            # 해당 게시물과 해당 유저의 좋아요 데이터를 취득
            heart = Heart.objects.filter(user=request.user.pk, board=board.index)
            # 데이터가 있는 경우 좋아요 삭제하고 좋아요 수를 감소
            if heart:
                heart[0].delete()
                board_dict = {"heart_count": board.heart_count - 1}
                board_serializer = BoardHeartSerializer(board, board_dict)
                if board_serializer.is_valid():
                    board_serializer.save()
                return Response({"msg": "좋아요 취소"}, status=status.HTTP_200_OK)
            # 데이터가 없는 경우 좋아요 추가하고 좋아요 수를 추가
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
