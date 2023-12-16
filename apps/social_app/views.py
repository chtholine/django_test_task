from django.contrib.auth import logout, authenticate, login
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Post
from .serializers import UserSerializer, PostSerializer, LikeSerializer
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Count


# --- Auth --- #

class SignUpAPIView(APIView):
    @swagger_auto_schema(
        request_body=UserSerializer
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user is not None:
                refresh = RefreshToken.for_user(user)
                response_data = {
                    "status": "success",
                    "message": "User created successfully.",
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(type=openapi.TYPE_STRING),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=["username", "password"],
        )
    )
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if username is not None:
            user = authenticate(
                request, username=username, password=password
            )
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                response_data = {
                    "status": "success",
                    "message": "Login successful.",
                    "data": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                }
                return Response(response_data, status=status.HTTP_200_OK)
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_400_BAD_REQUEST,
            )


class LogoutAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful."}, status=status.HTTP_200_OK)


# -- ViewSets -- #
class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: openapi.Response('List of users', schema=UserSerializer(many=True))})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: openapi.Response('Details of a user', schema=UserSerializer())})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path='activity', url_name='activity')
    def activity(self, request, pk=None):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        last_login = user.last_login
        last_request = timezone.now()
        user.save()

        return Response({
            'user_id': user.id,
            'last_login': last_login,
            'last_request': last_request
        })


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(responses={200: openapi.Response('List of posts', schema=PostSerializer(many=True))})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: openapi.Response('Details of a post', schema=PostSerializer())})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
            },
            required=['title', 'content'],
        ),
        responses={201: openapi.Response('Post created successfully', schema=PostSerializer())}
    )
    def create(self, request, *args, **kwargs):
        # Ensure user_id is included in request.data
        request.data['user'] = request.user.id

        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'title': openapi.Schema(type=openapi.TYPE_STRING),
            'content': openapi.Schema(type=openapi.TYPE_STRING),
        },
        required=['title', 'content'],
    ), responses={200: openapi.Response('Post updated successfully', schema=PostSerializer())})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={204: 'Post deleted successfully'})
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(request_body=LikeSerializer)
    @action(detail=True, methods=['post'], url_path='like', url_name='like')
    def like(self, request, pk=None):
        user = request.user
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = LikeSerializer(data=request.data)
        if serializer.is_valid():
            if user in post.liked_by.all():
                post.liked_by.remove(user)
                return Response({'message': f"Post '{post.title}' with id:{post.id} unliked successfully"},
                                status=status.HTTP_200_OK)
            else:
                post.liked_by.add(user)
                return Response({'message': f"Post '{post.title}' with id:{post.id} liked successfully"},
                                status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'date_from', openapi.IN_QUERY, description='Start date for analytics (YYYY-MM-DD)',
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter(
                'date_to', openapi.IN_QUERY, description='End date for analytics (YYYY-MM-DD)',
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ],
        responses={200: openapi.Response('Analytics data', schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
    )
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')

        # Default to the last 30 days if not specified
        if not date_from:
            date_from = timezone.now() - timezone.timedelta(days=30)
        if not date_to:
            date_to = timezone.now()

        analytics_data = (
            Post.objects
            .filter(liked_by__isnull=False,
                    created_at__range=[date_from, timezone.datetime.combine(date_to, timezone.datetime.max.time())])
            .annotate(likes_count=Count('liked_by'))
            .values('created_at__date')
            .annotate(total_likes=Count('liked_by'))
            .order_by('created_at__date')
        )

        return Response({'analytics': list(analytics_data)}, status=status.HTTP_200_OK)


class UserActivityViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        last_login = user.last_login
        last_request = timezone.now()

        user.save()  # Save user to update the last_request time

        return Response({
            'last_login': last_login,
            'last_request': last_request
        })
