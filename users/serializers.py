from rest_framework import serializers
from django.contrib.auth import get_user_model
from tweets.serializers import TweetSerializer  # Importando o TweetSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    tweets = TweetSerializer(many=True, read_only=True)  # Incluindo os tweets do usuário

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'tweets']  # Adicionando 'tweets'
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
