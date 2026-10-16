from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# 1. Custom JWT Payload[cite: 13]
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

# 2. Sample Authorized Endpoint[cite: 13]
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