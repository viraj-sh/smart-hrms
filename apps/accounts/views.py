from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

# 1. Custom JWT Payload[cite: 13]
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        return token

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