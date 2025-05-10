from rest_framework import serializers
from django.contrib.auth import get_user_model
from tweets.serializers import TweetSerializer
from .models import Follow  # Import necessário

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    tweets = TweetSerializer(many=True, read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'tweets',
            'followers_count',
            'following_count',
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def get_followers_count(self, obj):
        return Follow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        return Follow.objects.filter(follower=obj).count()

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
