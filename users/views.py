# users/views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Follow
from .serializers import UserSerializer

from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter


class UserViewSet(ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]  # Agora requer autenticação
    filter_backends = [SearchFilter]  
    search_fields = ['username']      # Buscar só por username

    @action(detail=False, methods=['post'], url_path='register', permission_classes=[AllowAny])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuário criado com sucesso'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user_id': user.id,
                'username': user.username,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'detail': 'Credenciais inválidas'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['post'], url_path='follow', permission_classes=[IsAuthenticated])
    def follow(self, request, pk=None):
        following_user = self.get_object()
        follower_user = request.user

        if follower_user == following_user:
            return Response({"detail": "Você não pode seguir a si mesmo."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário já está seguindo
        follow, created = Follow.objects.get_or_create(follower=follower_user, following=following_user)
        if created:
            return Response({"detail": f"Agora você está seguindo {following_user.username}."}, status=status.HTTP_201_CREATED)
        return Response({"detail": "Você já está seguindo esse usuário."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='unfollow', permission_classes=[IsAuthenticated])
    def unfollow(self, request, pk=None):
        following_user = self.get_object()
        follower_user = request.user

        if follower_user == following_user:
            return Response({"detail": "Você não pode deixar de seguir a si mesmo."}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se o usuário segue o outro
        follow = Follow.objects.filter(follower=follower_user, following=following_user).first()
        if follow:
            follow.delete()
            return Response({"detail": f"Você deixou de seguir {following_user.username}."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Você não está seguindo esse usuário."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='is_following', permission_classes=[IsAuthenticated])
    def is_following(self, request, pk=None):
        try:
            target_user = self.get_object()
            current_user = request.user
            is_following = Follow.objects.filter(follower=current_user, following=target_user).exists()
            return Response({"is_following": is_following})
        except CustomUser.DoesNotExist:
            return Response({"detail": "Usuário não encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'], url_path='followers', permission_classes=[IsAuthenticated])
    def followers(self, request, pk=None):
        user = self.get_object()
        followers = CustomUser.objects.filter(following__following=user)
        serializer = UserSerializer(followers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='following', permission_classes=[IsAuthenticated])
    def following(self, request, pk=None):
        user = self.get_object()
        following = CustomUser.objects.filter(followers__follower=user)
        serializer = UserSerializer(following, many=True)
        return Response(serializer.data)
