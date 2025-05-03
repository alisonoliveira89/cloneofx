from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tweet
from .serializers import TweetSerializer

class TweetViewSet(ModelViewSet):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Tweet.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='feed', permission_classes=[IsAuthenticatedOrReadOnly])
    def feed(self, request):
        user = request.user
        if user.is_authenticated:
            # Exibe tweets do próprio usuário; você pode expandir para "seguidos"
            tweets = Tweet.objects.filter(user=user)
        else:
            tweets = Tweet.objects.none()
        serializer = self.get_serializer(tweets, many=True)
        return Response(serializer.data)
