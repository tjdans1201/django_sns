from dataclasses import field
from unittest.util import _MAX_LENGTH
from rest_framework import serializers
from .models import Board
import datetime


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["writer", "title", "content", "hashtag"]
