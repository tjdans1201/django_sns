from django.urls import path, include
from .views import BoardAPI, BoardsAPI

urlpatterns = [path("", BoardsAPI.as_view()), path("/<int:id>", BoardAPI.as_view())]
