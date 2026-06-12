from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from apps.core.jwt_utils import create_access_token, create_refresh_token, decode_token
from apps.user.models import CustomUser, FrequentPassenger
from apps.user.serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    FrequentPassengerSerializer,
)


class UserRegistrationView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'access': create_access_token(user),
                'refresh': create_refresh_token(user),
                'message': '注册成功'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'token': token.key,
                'access': create_access_token(user),
                'refresh': create_refresh_token(user),
                'message': '登录成功'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TokenRefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'error': '缺少 refresh token'}, status=400)
        try:
            payload = decode_token(refresh)
            if payload.get('type') != 'refresh':
                return Response({'error': 'Token 类型错误'}, status=400)
            user = CustomUser.objects.get(pk=payload['user_id'], is_active=True)
            return Response({
                'access': create_access_token(user),
                'refresh': create_refresh_token(user),
            })
        except Exception:
            return Response({'error': '无效的 refresh token'}, status=400)


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            request.user.auth_token.delete()
        except Exception:
            pass
        return Response({'message': '退出成功'})


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FrequentPassengerListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FrequentPassengerSerializer

    def get_queryset(self):
        return FrequentPassenger.objects.filter(user=self.request.user)


class FrequentPassengerDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FrequentPassengerSerializer

    def get_queryset(self):
        return FrequentPassenger.objects.filter(user=self.request.user)
