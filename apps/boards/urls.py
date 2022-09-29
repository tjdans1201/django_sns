from django.urls import path, include

from .views import BoardAPI, BoardsAPI, give_heart

# from . import views

urlpatterns = [
    path("/<int:id>/heart", give_heart),
    path("", BoardsAPI.as_view()),
    path("/<int:id>", BoardAPI.as_view()),
]
