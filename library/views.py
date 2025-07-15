from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book, CustomUser
from .serializers import BookSerializer, UserRegistrationSerializer, UserSerializer
from .utils import send_magic_link
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class RegisterUserView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            send_magic_link(user)
            return Response({'message': 'Usuario creado y magic link enviado'}, status=201)
        return Response(serializer.errors, status=400)


class MagicLoginView(APIView):
    def get(self, request):
        token = request.query_params.get('token')
        signer = TimestampSigner()
        try:
            user_id = signer.unsign(token, max_age=3600)
            user = CustomUser.objects.get(pk=user_id)

            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": user_serializer.data
            })

        except (BadSignature, SignatureExpired):
            return Response({"error": "Token inválido o expirado"}, status=400)

class ResendMagicLinkView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            user = CustomUser.objects.get(email=email)
            send_magic_link(user)
            return Response({'message': 'Magic link reenviado'}, status=200)
        except get_user_model().DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)
