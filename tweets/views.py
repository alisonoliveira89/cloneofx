from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Tweet
from .serializers import TweetSerializer
from users.models import CustomUser  # Importando o modelo de usuário
from users.models import Follow  # Importando o modelo de Follow

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
            # Buscar os usuários que o usuário está seguindo
            followed_users = Follow.objects.filter(follower=user).values('following')  # IDs dos usuários seguidos
            # Adicionar o próprio usuário na busca (tweets do próprio usuário)
            followed_users_ids = list(followed_users) + [user.id]
            
            # Buscar tweets do próprio usuário e dos usuários seguidos
            tweets = Tweet.objects.filter(user__id__in=followed_users_ids)
        else:
            tweets = Tweet.objects.none()
        
        serializer = self.get_serializer(tweets, many=True)
        return Response(serializer.data)
