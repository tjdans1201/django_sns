from django.test import TestCase
from rest_framework.test import APIClient
import os
from ..boards.models import Board, Hashtag
from datetime import datetime
import pandas as pd
import json

curDir = os.path.dirname(os.path.normpath(__file__))

# 더미데이터 생성
def set_dummy(table_list):
    for i in table_list:
        df = pd.read_csv(curDir + "/dummy/" + i + ".csv")
        i_dict_list = df.to_dict("records")
        if i == "board":
            boards = [
                Board(
                    index=x["index"],
                    title=x["title"],
                    content=x["content"],
                    created_at=x["created_at"],
                    heart_count=x["heart_count"],
                    views_count=x["views_count"],
                    is_active=x["is_active"],
                    writer_id=x["writer_id"],
                )
                for x in i_dict_list
            ]
            Board.objects.bulk_create(boards)
        elif i == "hashtag":
            hashtags = [Hashtag(id=x["id"], tag_content=x["tag_content"]) for x in i_dict_list]
            Hashtag.objects.bulk_create(hashtags)
        print("finish insert table " + i)


class TestViews(TestCase):
    @classmethod
    def setUp(cls):
        pass

    def test_users(self):
        # 회원가입 테스트
        client = APIClient()

        result = client.post(
            "/api/users/register",
            data={
                "email": "test@google.com",
                "nickname": "test_nick",
                "password": "password1234!",
                "password2": "password1234!",
            },
        )
        exp = {"email": "test@google.com", "nickname": "test_nick"}
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.data, exp)

        # 로그인 테스트
        # case_1 실패

        result = client.post(
            "/api/users/login",
            data={
                "email": "test@google.com",
                "password": "password1234@",
            },
        )
        exp = {"message": "email 또는 password가 틀렸습니다."}
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, exp)

        # case_2 성공
        result = client.post(
            "/api/users/login",
            data={
                "email": "test@google.com",
                "password": "password1234!",
            },
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data["msg"], "로그인에 성공했습니다.")
        self.assertTrue("access_token" in result.data["jwt_token"].keys())
        self.assertTrue("refresh_token" in result.data["jwt_token"].keys())

    def test_boards(self):
        # User(email="test@test.com", nickname="test_nick", password="test1234!").save()
        # print(User.objects.all().first())
        client = APIClient()
        # 유저등록_유저1
        result = client.post(
            "/api/users/register",
            data={
                "email": "test1@test.com",
                "nickname": "test_nick1",
                "password": "test1234!",
                "password2": "test1234!",
            },
        )
        # 유저등록_유저2
        result = client.post(
            "/api/users/register",
            data={
                "email": "test2@test.com",
                "nickname": "test_nick2",
                "password": "test1234!",
                "password2": "test1234!",
            },
        )
        # 토큰 취득
        result = client.post(
            "/api/users/login",
            data={
                "email": "test1@test.com",
                "password": "test1234!",
            },
        )
        access_token_1 = result.data["jwt_token"]["access_token"]
        # 토큰 취득
        result = client.post(
            "/api/users/login",
            data={
                "email": "test2@test.com",
                "password": "test1234!",
            },
        )
        access_token_2 = result.data["jwt_token"]["access_token"]
        # 게시글 등록
        # case_1 토큰 없음
        result = client.post(
            "/api/boards",
            data={"title": "test", "content": "test", "hashtag": "#first"},
            format="json",
        )
        self.assertEqual(result.status_code, 401)
        # case_2 정상 등록
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_1)
        result = client.post(
            "/api/boards",
            data={"title": "test", "content": "test", "hashtag": "#first"},
            format="json",
        )
        exp = {"msg": "게시글이 등록되었습니다."}
        self.assertEqual(result.status_code, 201)
        self.assertEqual(result.data, exp)
        registered_board = Board.objects.get(index=1)
        exp = {
            "title": "test",
            "content": "test",
            "hashtag": "#first",
            "heart_count": 0,
            "views_count": 0,
        }
        registered_board_dict = {
            "title": registered_board.title,
            "content": registered_board.content,
            "hashtag": ",".join(["#" + i.tag_content for i in registered_board.tagging.all()]),
            "heart_count": registered_board.heart_count,
            "views_count": registered_board.views_count,
        }
        self.assertEqual(registered_board_dict, exp)
        # 게시글 상세 조회
        result = client.get("/api/boards/1")
        exp = {
            "title": "test",
            "content": "test",
            "hashtag": "#first",
            "heart_count": 0,
            "views_count": 1,
            "writer": "test_nick1",
            "created_at": str(datetime.now().date()),
        }
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)
        # 게시글 좋아요 기능
        # case_1 좋아요
        result = client.patch("/api/boards/1/heart")
        registered_board = Board.objects.get(index=1)
        self.assertEqual(registered_board.heart_count, 1)
        # case_2 다른 유저가 좋아요 추가
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_2)
        result = client.patch("/api/boards/1/heart")
        registered_board = Board.objects.get(index=1)
        self.assertEqual(registered_board.heart_count, 2)
        # case_3 좋아요 취소
        result = client.patch("/api/boards/1/heart")
        registered_board = Board.objects.get(index=1)
        self.assertEqual(registered_board.heart_count, 1)

        # 게시글 수정 기능
        # case_1 수정권한 없음
        result = client.put(
            "/api/boards/1",
            data={"title": "modify_test", "content": "modify_test", "hashtag": "#first,#modify"},
            format="json",
        )
        print(result)
        exp = {"msg": "게시글 수정 권한이 없습니다."}
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.data, exp)
        # case_2 수정성공
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_1)
        result = client.put(
            "/api/boards/1",
            data={"title": "modify_test", "content": "modify_test", "hashtag": "#first,#modify"},
            format="json",
        )
        exp = {"msg": "게시글이 수정되었습니다."}
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)
        registered_board = Board.objects.get(index=1)
        exp = {
            "title": "modify_test",
            "content": "modify_test",
            "hashtag": "#first,#modify",
            "heart_count": 1,
            "views_count": 1,
        }
        registered_board_dict = {
            "title": registered_board.title,
            "content": registered_board.content,
            "hashtag": ",".join(["#" + i.tag_content for i in registered_board.tagging.all()]),
            "heart_count": registered_board.heart_count,
            "views_count": registered_board.views_count,
        }
        self.assertEqual(registered_board_dict, exp)
        # 게시글 삭제(soft_delete)
        # case_1 권한 없음
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_2)
        result = client.delete("/api/boards/1")
        exp = {"msg": "게시글 삭제 권한이 없습니다."}
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.data, exp)
        # case_2 삭제 성공
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_1)
        result = client.delete("/api/boards/1")
        exp = {"msg": "게시글이 삭제되었습니다."}
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)
        registered_board = Board.objects.filter(index=1, is_active=True).first()
        self.assertEqual(registered_board, None)
        # 게시글 복구
        # case_1 권한 없음
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_2)
        result = client.patch("/api/boards/1")
        exp = {"msg": "게시글 복구 권한이 없습니다."}
        self.assertEqual(result.status_code, 401)
        self.assertEqual(result.data, exp)
        # case_2 복구 성공
        client.credentials(HTTP_AUTHORIZATION="Bearer " + access_token_1)
        result = client.patch("/api/boards/1")
        exp = {"msg": "게시글이 복구되었습니다."}
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.data, exp)
        registered_board = Board.objects.filter(index=1, is_active=True).first()
        self.assertTrue(registered_board is not None)

        set_dummy(["board", "hashtag"])
        hash_tag_dict = {}
        for idx, val in enumerate(list(Hashtag.objects.all())):
            hash_tag_dict[idx + 1] = val
        for i in Board.objects.all().order_by("index"):
            # 2~4 #서울
            if i.index >= 2 and i.index < 5:
                i.tagging.add(hash_tag_dict[3])
            # 5~7 #맛집
            if i.index >= 5 and i.index < 8:
                i.tagging.add(hash_tag_dict[4])
            # 8~9 #서울맛집
            if i.index >= 8 and i.index < 10:
                i.tagging.add(hash_tag_dict[5])
            # 10~11 #서울,#맛집
            if i.index >= 10:
                i.tagging.add(hash_tag_dict[3])
                i.tagging.add(hash_tag_dict[4])
            i.save()

        # 리스트 취득
        # 총 게시글 갯수 11개
        board_list = Board.objects.all()
        self.assertEqual(len(board_list), 11)
        # case_1 실패(page parameter 없음)
        result = client.get("/api/boards")
        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.data, {"msg": "page를 지정해주세요."})
        # case_2 성공(page parameter 1) 10개 취득
        result = client.get("/api/boards?page=1")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 1,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_3 성공(page parameter 1, orderby: 페이지 뷰) 10개 취득
        result = client.get("/api/boards?page=1&orderBy=-views_count")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "modify_test",
                    "content": "modify_test",
                    "hashtag": "#first,#modify",
                    "heart_count": 1,
                    "views_count": 1,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 1,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_4 성공(page parameter 2) 1개 취득
        result = client.get("/api/boards?page=2")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "modify_test",
                    "content": "modify_test",
                    "hashtag": "#first,#modify",
                    "heart_count": 1,
                    "views_count": 1,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                }
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_5 성공(search : 테스트) 2개 취득
        result = client.get("/api/boards?page=1&search=테스트")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#맛집",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_6 성공(hashtags : 서울) 5개 취득(index:2,3,4,10,11)
        result = client.get("/api/boards?page=1&hashtags=서울")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 1,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_7 성공(hashtags : 서울맛집) 2개 취득(index:8,9)
        result = client.get("/api/boards?page=1&hashtags=서울맛집")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_8 성공(hashtags : 서울, 맛집) 2개 취득(index:10,11)
        result = client.get("/api/boards?page=1&hashtags=서울,맛집")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
                {
                    "title": "안녕",
                    "content": "test입니다",
                    "hashtag": "#서울,#맛집",
                    "heart_count": 1,
                    "views_count": 0,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                },
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        # case_9 성공(search : 테스트, hashtags : 서울) 1개 취득
        result = client.get("/api/boards?page=1&search=테스트&hashtags=서울")
        self.assertEqual(result.status_code, 200)
        exp = {
            "board_list": [
                {
                    "title": "테스트",
                    "content": "test입니다",
                    "hashtag": "#서울",
                    "heart_count": 0,
                    "views_count": 2,
                    "writer": "test_nick1",
                    "created_at": str(datetime.now().date()),
                }
            ]
        }
        self.assertEqual(json.loads(result.data), exp)
        print("finish")
