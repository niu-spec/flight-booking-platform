import jwt
from django.contrib.auth import get_user_model
from rest_framework import authentication, exceptions

from apps.core.jwt_utils import decode_token

User = get_user_model()


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).decode('utf-8')
        if not auth:
            return None
        parts = auth.split()
        if len(parts) != 2 or parts[0] != self.keyword:
            return None
        try:
            payload = decode_token(parts[1])
        except jwt.PyJWTError:
            # JWT 过期或无效时返回 None，让 Token 认证继续尝试
            return None
        if payload.get('type') != 'access':
            raise exceptions.AuthenticationFailed('Token 类型错误')
        try:
            user = User.objects.get(pk=payload['user_id'], is_active=True)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('用户不存在')
        return user, parts[1]
