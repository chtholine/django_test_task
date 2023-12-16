from rest_framework import serializers
from .models import User, Post


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user


class PostSerializer(serializers.ModelSerializer):
    liked_by = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'created_at', 'liked_by']
        read_only_fields = ['user']

    def create(self, validated_data):
        # Ensure the user is set before creating the post
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)


class LikeSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()
