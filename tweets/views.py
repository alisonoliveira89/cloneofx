from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tweet, Like, Comment
from .serializers import TweetSerializer, CommentSerializer
from users.models import CustomUser  # Importando o modelo de usuário
from users.models import Follow  # Importando o modelo de Follow

class TweetViewSet(ModelViewSet):
    serializer_class = TweetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return Tweet.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        tweet = self.get_object()
        if tweet.user != request.user:
            return Response({'detail': 'Você não pode excluir este tweet.'}, status=403)
        return super().destroy(request, *args, **kwargs)



    # /api/tweets/feed/
    @action(detail=False, methods=['get'], url_path='feed', permission_classes=[IsAuthenticatedOrReadOnly])
    def feed(self, request):
        user = request.user
        if user.is_authenticated:
            # Obtém os usuários que o usuário logado segue
            followed_users = Follow.objects.filter(follower=user).values_list('following', flat=True)

            # Retorna tweets dessas pessoas
            tweets = Tweet.objects.filter(user__in=followed_users).order_by('-created_at')
        else:
            tweets = Tweet.objects.none()
        
        serializer = self.get_serializer(tweets, many=True)
        return Response(serializer.data)

    # /api/tweets/my/
    @action(detail=False, methods=['get'], url_path='my', permission_classes=[IsAuthenticatedOrReadOnly])
    def my_tweets(self, request):
        user = request.user
        if user.is_authenticated:
            tweets = Tweet.objects.filter(user=user).order_by('-created_at')
        else:
            tweets = Tweet.objects.none()

        serializer = self.get_serializer(tweets, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        tweet = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, tweet=tweet)
        if not created:
            like.delete()
            return Response({'liked': False})
        return Response({'liked': True})

    @action(detail=True, methods=['post'])
    def comment(self, request, pk=None):
        tweet = self.get_object()
        comment = Comment.objects.create(
            user=request.user,
            tweet=tweet,
            content=request.data.get('content')
        )
        return Response(CommentSerializer(comment).data)

    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        tweet = self.get_object()
        comments = tweet.comments.all().order_by('-created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

