from dataclasses import field
from unittest.util import _MAX_LENGTH
from rest_framework import serializers
from .models import Board, Heart
import datetime


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["writer", "title", "content", "hashtag"]


class BoardListSerailizer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    writer = serializers.SerializerMethodField()
    hashtag = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "title",
            "content",
            "hashtag",
            "heart_count",
            "views_count",
            "writer",
            "created_at",
        ]

    def get_created_at(self, obj):
        print(obj)
        created_date = datetime.datetime.strftime(obj.created_at, "%Y-%m-%d")
        return created_date

    def get_writer(self, obj):
        writer_nickname = obj.writer.nickname
        print(obj)
        return writer_nickname

    def get_hashtag(self, obj):
        hashtag_list = obj.hashtag.split(",")
        hashtag = ",".join(["#" + i for i in hashtag_list])
        return hashtag


class HeartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heart
        fields = [
            "index",
            "user",
            "Heart",
        ]
