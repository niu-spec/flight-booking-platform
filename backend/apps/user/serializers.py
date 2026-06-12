from rest_framework import serializers
from django.contrib.auth import authenticate
from apps.user.models import CustomUser, FrequentPassenger


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'password', 'password_confirm', 'email', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': '密码不匹配'})
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    data['user'] = user
                else:
                    raise serializers.ValidationError('用户账号已被禁用')
            else:
                raise serializers.ValidationError('用户名或密码错误')
        else:
            raise serializers.ValidationError('必须提供用户名和密码')
        
        return data


class UserSerializer(serializers.ModelSerializer):
    member_level = serializers.ReadOnlyField()
    member_label = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'phone', 'email', 'first_name', 'last_name',
            'date_joined', 'is_staff', 'points', 'member_level', 'member_label',
        ]
        read_only_fields = ['id', 'date_joined', 'is_staff', 'points', 'member_level', 'member_label']


class FrequentPassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequentPassenger
        fields = ['id', 'name', 'id_card', 'phone', 'is_default', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        user = self.context['request'].user
        if validated_data.get('is_default'):
            FrequentPassenger.objects.filter(user=user, is_default=True).update(is_default=False)
        return FrequentPassenger.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        if validated_data.get('is_default'):
            FrequentPassenger.objects.filter(user=instance.user, is_default=True).exclude(
                pk=instance.pk
            ).update(is_default=False)
        return super().update(instance, validated_data)
