from django.urls import path, include
from .views import RegisterView, LoginAPI

urlpatterns = [path("/register", RegisterView.as_view()), path("/login", LoginAPI.as_view())]
