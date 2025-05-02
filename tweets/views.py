from rest_framework.viewsets import ModelViewSet
from .models import Tweet
from .serializers import TweetSerializer
from rest_framework.permissions import IsAuthenticated

class TweetViewSet(ModelViewSet):
    queryset = Tweet.objects.all().order_by('-created_at')
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
