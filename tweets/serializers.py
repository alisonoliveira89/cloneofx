from rest_framework import serializers
from .models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ['id', 'content', 'created_at', 'author']
        read_only_fields = ['author', 'created_at']
