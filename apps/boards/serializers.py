from rest_framework import serializers
from .models import Board, Heart
import datetime


class BoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["writer", "title", "content", "tagging"]

    def create(self, validated_data):
        tag_list = validated_data.pop("tagging")
        board = Board.objects.create(**validated_data)
        for i in tag_list:
            board.tagging.add(i)
        return board


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
        created_date = datetime.datetime.strftime(obj.created_at, "%Y-%m-%d")
        return created_date

    def get_writer(self, obj):
        writer_nickname = obj.writer.nickname
        return writer_nickname

    def get_hashtag(self, obj):
        hashtag_list = obj.tagging.all()
        hashtag_list = [i.tag_content for i in hashtag_list]
        hashtag = ",".join(["#" + i for i in hashtag_list])
        return hashtag


class HeartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Heart
        fields = [
            "user",
            "board",
        ]

    def create(self, validated_data):
        return Heart.objects.create(**validated_data)


class BoardHeartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["heart_count"]

    def update(self, instance, validated_data):
        instance.heart_count = validated_data.get("heart_count", instance.heart_count)
        instance.save()
        return instance


class BoardSoftDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Board
        fields = ["is_active"]

    def update(self, instance, validated_data):
        instance.is_active = validated_data.get("is_active", instance.is_active)
        instance.save()
        return instance
