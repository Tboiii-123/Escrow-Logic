from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes,throttle_classes
# Create your views here.
from .serializers import RegisterSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User




@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
   

    serializer =RegisterSerializer(data=request.data)
    if serializer.is_valid():
        register=serializer.save()
      

        return Response({
             "message": "User registered successfully ",
            "data": serializer.data
        }, status =201)
    print(serializer.errors)
    return Response({
        "error":serializer.errors
    }, status=400)





@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
        
    try:
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"detail": "Logout successful"})
    except Exception as e:
        print(str(e))
        return Response({"error": str(e)}, status=400)
       

