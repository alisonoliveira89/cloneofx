from rest_framework import serializers
from .models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Tweet
        fields = ['id', 'user', 'username', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']
