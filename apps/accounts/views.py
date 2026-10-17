from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser
from .permissions import IsAdmin, IsHR, IsAdminOrHR

# 1. Custom JWT Login Payload (Claims on Access Token Only)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        access_token['email'] = self.user.email
        access_token['role'] = self.user.role
        data['access'] = str(access_token)
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 2. Custom JWT Refresh Payload (Injects claims into fresh Access Token)
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh_token_str = data.get('refresh', attrs['refresh'])
        refresh = RefreshToken(refresh_token_str)
        user = CustomUser.objects.get(id=refresh['user_id'])
        access_token = refresh.access_token
        access_token['email'] = user.email
        access_token['role'] = user.role
        data['access'] = str(access_token)
        return data

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

# 3. Sample Authorized Endpoint
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_auth_endpoint(request):
    user = request.user
    return Response({
        "message": "You are successfully authenticated!",
        "user_data": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    })

# 4. Role-based Test Endpoints
@api_view(['GET'])
@permission_classes([IsAdmin])
def test_admin_access(request):
    return Response({"message": "Welcome Admin. You have Admin-level access."})

@api_view(['GET'])
@permission_classes([IsHR])
def test_hr_access(request):
    return Response({"message": "Welcome HR. You have HR-level access."})

@api_view(['GET'])
@permission_classes([IsAdminOrHR])
def test_admin_or_hr_access(request):
    return Response({"message": "Welcome. You have Admin or HR access."})