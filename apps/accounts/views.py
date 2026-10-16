from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser

# 1. Custom JWT Login Payload (Claims on Access Token Only)
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        # Call the parent method to get the default tokens
        data = super().validate(attrs)
        
        # Get the refresh token and access token objects
        refresh = self.get_token(self.user)
        access_token = refresh.access_token
        
        # Add custom claims ONLY to the access token
        access_token['email'] = self.user.email
        access_token['role'] = self.user.role
        
        # Update the access token string in the response data
        data['access'] = str(access_token)
        
        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# 2. Custom JWT Refresh Payload (Injects claims into fresh Access Token)
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        # Run the default validation which handles rotation
        data = super().validate(attrs)
        
        # Get the active refresh token (handles both rotated and non-rotated setups)
        refresh_token_str = data.get('refresh', attrs['refresh'])
        refresh = RefreshToken(refresh_token_str)
        
        # Fetch the user to get current email and role
        user = CustomUser.objects.get(id=refresh['user_id'])
        
        # Generate a fresh access token and attach the custom claims
        access_token = refresh.access_token
        access_token['email'] = user.email
        access_token['role'] = user.role
        
        # Replace the default access token with our custom one
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