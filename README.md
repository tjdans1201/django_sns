# django_sns

## 프로젝트 설명
- SNS의 기본적인 기능을 가진 API 개발
- 로그인을 하면 JWT토큰을 발급하여 기능 이용 시 토큰으로 유저 식별 
- 게시글 목록 조회, 상세 조회, 수정, 좋아요, 삭제, 복구 등의 기능을 제공
- 해시태그 또는 키워드로 게시글을 검색할 수 있음
- pagination을 사용하여 한 페이지당 보여지는 게시글 수 조정

## 사용된 기술
 - **Back-End** : Python, Django, Django REST framework
 - **Database** : sqlite3

## ERD

<img width="196" alt="erd" src="https://user-images.githubusercontent.com/57758265/192914377-e8075b32-127e-4982-851c-dba9b3b82cac.png">

## API

### 회원가입 API

- 이메일을 ID로 사용한다.

method : post

api/users/register

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 이메일 | email | str |  |
| 닉네임 | nickname | str |  |
| 패스워드 | password | str |  |
| 확인용 패스워드 | password2 | str |  |

Request Example

```json
{"email":"test@google.com", "nickname":"test", "password":"test_pass", "password2":"test_pass"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 이메일 | email | str |  |
| 닉네임 | nickname | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 201 | - |  | 정상종료 |
| 400 | Request Error |  | Request Body 문제 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 201

```json
{"email": "test@google.com", "nickname": "test"}
```

2) 400

```json
{
    "message": "리퀘스트 에러가 발생했습니다."
}
```

3) 500

```json
{
    "message": "서버 에러가 발생하였습니다."
}
```

### 로그인 API

- JWT 토큰을 발급받으며, 이를 추후 사용자 인증으로 사용

method : post

api/users/login

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 이메일 | email | str |  |
| 패스워드 | password | str |  |

Request Example

```json
{"email":"test@google.com", "password":"test_pass"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |
| jwt토큰 | jwt_token | dict |  |
| access토큰 | access_token | dict |  |
| refresh토큰 | refresh_token | dict |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - |  | 정상종료 |
| 400 | Request Error | "email 또는 password가 틀렸습니다." | Request Body 문제 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": '로그인에 성공했습니다.', 'jwt_token': {'access_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjY0MzY2NTY0LCJpYXQiOjE2NjQzNjQ3NjQsImp0aSI6ImMxY2UxNTI1YjlmOTQ0OTc5Y2ZiYmI1ZTUxNjZlMjhlIiwidXNlcl9pZCI6MX0.KuxKnUl5OqC7lH9di4r6ahdSJk_1c578oq7Xds819pE', 'refresh_token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTY2NDk2OTU2NCwiaWF0IjoxNjY0MzY0NzY0LCJqdGkiOiI3ZmZmYjNmMWVmZmU0MWNmODA3MTI3MTk2YzNiZjA0NyIsInVzZXJfaWQiOjF9.g7qCKtXHNt_KX13C6sHg2N1Bm0AoF44pddgsD3no2Es'}}
```

2) 400

```json
{
    "msg": "email 또는 password가 틀렸습니다."
}
```

3) 500

```json
{
    "msg": "서버 에러가 발생하였습니다."
}
```

## 게시글

- 모든 API는 헤더에 Access 토큰이 있어야 동작

### 게시글 등록 API

- 제목, 내용, 해시태그를 입력하여 생성

- 해시태그는 여러 개 등록 가능 ex) #서울,#맛집

- 게시글 모델의 해시태그 필드는 many to many 필드로 생성하여 여러개를 저장 및 검색 가능

method : post

api/boards

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 제목 | title | str |  |
| 내용 | content | str |  |
| 해시태그 | hashtag | str | #태그,#태그 형식 |

Request Example

```json
{"email":"test@google.com", "password":"test_pass"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | "게시글이 등록되었습니다.” | 정상종료 |
| 400 | Request Error | "필수 입력 항목이 부족합니다.”, “해시태그 형식이 틀렸습니다” | Request Body 문제 |
| 401 | Permission Error |  | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": "게시글이 등록되었습니다."}
```

2) 400

```json
{
 "msg": "필수 입력 항목이 부족합니다."
}
```

3) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 수정 API

- 제목, 내용, 해시태그를 수정

- 작성자만 게시글을 수정 가능

method : put

api/boards/<int:index>

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Request Body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 제목 | title | str |  |
| 내용 | content | str |  |
| 해시태그 | hashtag | str | #태그,#태그 형식 |

Request Example

```json
{"email":"test@google.com", "password":"test_pass"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | "게시글이 등록되었습니다.” | 정상종료 |
| 400 | Request Error | "필수 입력 항목이 부족합니다.”, “해시태그 형식이 틀렸습니다” | Request Body 문제 |
| 401 | Permission Error | “게시글 수정 권한이 없습니다.” | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": "게시글이 수정되었습니다."}
```

2) 400

```json
{
 "msg": "필수 입력 항목이 부족합니다."
}
```

3) 401

```json
{
 "msg": "게시글 수정 권한이 없습니다."
}
```

4) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 삭제 API

- 게시글을 삭제

- 작성자만 게시글을 삭제 가능

- 게시글은 언제든지 복구 가능

soft_delete방식으로 게시글 테이블의 is_active 필드를 True에서 False로 변경하여 삭제 처리

method : delete

api/boards/<int:index>

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | "게시글이 삭제되었습니다.” | 정상종료 |
| 401 | Permission Error | “게시글 삭제 권한이 없습니다.” | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": "게시글이 삭제되었습니다."}
```

2) 401

```json
{
 "msg": "게시글 삭제 권한이 없습니다."
}
```

3) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 복구 API

게시글을 복구

작성자만 게시글을 복구 가능

게시글 테이블의 is_active 필드를 False 에서 True로 변경하여 삭제 처리

method : patch

api/boards/<int:index>

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | "게시글이 복구되었습니다.” | 정상종료 |
| 401 | Permission Error | “게시글 복구 권한이 없습니다.” | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": "게시글이 복구되었습니다."}
```

2) 401

```json
{
 "msg": "게시글 복구 권한이 없습니다."
}
```

3) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 상세 조회 API

- 해당 게시글을 조회

- 토큰이 있는 모든 유저에게 보기권한이 있음

- 작성자를 포함한 모든 사용자는 게시글에 좋아요를 누를 수 있음.

- 해당 유저가 좋아요를 누른 상태에서 다시 좋아요를 누르면 취소(좋아요 기능은 별도의 API에서 구현)

- 작성자를 포함한 모든 유저가 게시글을 조회했을 때 해당 게시글의 조회수가 1 증가

method : get

api/boards/<int:index>

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
|  | {} | dict |  |
| 제목 | title | str |  |
| 내용 | content | str |  |
| 해시태그 | hashtag | str |  |
| 좋아요 수 | heart_count | int |  |
| 조회수 | view_count | int |  |
| 작성자 | writer | str | 작성자 닉네임 |
| 작성일 | created_at | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - |  | 정상종료 |
| 401 | Permission Error |  | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{
            "title": "test",
            "content": "test",
            "hashtag": "#first",
            "heart_count": 0,
            "views_count": 1,
            "writer": "test_nick1",
            "created_at": "2022-09-28",
}
```

2) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 좋아요/좋아요 취소 API

- 게시글에 좋아요 또는 좋아요를 취소할 수 있음

- 유저는 해당 게시물에 한번만 좋아요 가능

- 좋아요를 누른 유저가 다시 좋아요를 누르면 좋아요가 취소

- 유저가 좋아요를 누르면 좋아요 테이블에서 해당 유저와 해당 게시물의 데이터를 조회 후

- 데이터가 없으면 좋아요 수를 증가시키고 좋아요 테이블에 해당 데이터를 추가

- 데이터가 있으면 좋아요 수를 감소시키고 좋아요 테이블에서 해당 데이터를 삭제

method : patch

api/boards/<int:index>/heart

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 메시지 | msg | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - | "좋아요.”, “좋아요 취소” | 정상종료 |
| 401 | Permission Error |  | 인증 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"msg": "좋아요"}
```

2) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

### 게시글 목록 조회 API

게시글 목록을 조회

토큰이 있는 모든 유저에게 보기권한이 있음

게시글 목록에는 제목, 작성자, 해시태그, 작성일, 좋아요 수, 조회수 가 포함

Pagination 기능으로 한 페이지에 10개씩 리턴(페이지 지정 필수)

사용자는 입력한 키워드로 제목에 해당 키워드를 포함한 게시물을 조회 가능(선택)

사용자는 지정한 키워드로 해시태그에 해당 키워드를 포함한 게시물을 필터링 가능(선택)

[ex. “서울” 검색 시 > #서울(검색됨) / #서울맛집 (검색안됨)  / #서울,#맛집(검색됨)]
[ex. “서울,맛집” 검색 시 > #서울(검색안됨) / #서울맛집 (검색안됨)  / #서울,#맛집(검색됨)]

사용자는 게시글의 정렬 순서를 작성일, 좋아요 수, 조회 수로 지정할 수 있음(기본적으로 작성일 기준)(선택)

method : get

api/boards/<int:index>?page=&orderBy&search=?&hashtags=

Request header

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 인증 | Authorization |  |  |

Request Example

```json
{"Authorization":"Bearer {access_token}"}
```

Query Param

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 페이지 | page | int | 필수 |
| 정렬 기준 | orderBy | str |  |
| 검색어 | search | str |  |
| 해시태그 | hashtags | str | 여러개 지정 가능 |

Response_body

| 명칭 | 변수명 | 형태 | 비고 |
| --- | --- | --- | --- |
| 게시글 목록 | board_list | [] |  |
|  | {} | dict |  |
| 제목 | title | str |  |
| 내용 | content | str |  |
| 해시태그 | hashtag | str |  |
| 좋아요 수 | heart_count | int |  |
| 조회수 | view_count | int |  |
| 작성자 | writer | str | 작성자 닉네임 |
| 작성일 | created_at | str |  |

HTTP status code

| HTTP status | AppErrors | 메시지 | 설명 |
| --- | --- | --- | --- |
| 200 | - |  | 정상종료 |
| 400 | Request Error | "page를 지정해주세요.” | 리퀘스트 에러 |
| 500 | Internal Server Error | "서버 에러가 발생하였습니다.” | API 내부 에러 발생 |

Response Example

1) 200

```json
{"board_list":[
{
            "title": "test",
            "content": "test",
            "hashtag": "#first",
            "heart_count": 0,
            "views_count": 1,
            "writer": "test_nick1",
            "created_at": "2022-09-28",
},
{
            "title": "test2",
            "content": "test2",
            "hashtag": "#first",
            "heart_count": 0,
            "views_count": 1,
            "writer": "test_nick2",
            "created_at": "2022-09-28",
}
]
}
```

2) 400

```json
{
 "msg": "page를 지정해주세요."
}
```

3) 500

```json
{
 "msg": "서버 에러가 발생하였습니다."
}
```

## unittest
<img width="452" alt="화면 캡처 2022-09-21 200021" src="https://user-images.githubusercontent.com/57758265/192915204-7227fad4-09eb-49c1-b7a0-ca8a243d2ad0.jpeg">
