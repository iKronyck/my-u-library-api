from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book, CustomUser, BookLoan
from .serializers import BookSerializer, UserRegistrationSerializer, UserSerializer, BookLoanSerializer, MyLoanSerializer, ActivitySerializer
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

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


class BookLoanViewSet(viewsets.ModelViewSet):
    queryset = BookLoan.objects.all()
    serializer_class = BookLoanSerializer


class LoanBookView(APIView):
    def post(self, request):
        book_id = request.data.get('book_id')
        user_id = request.data.get('user_id')
        due_date = request.data.get('due_date')

        try:
            book = Book.objects.get(pk=book_id)
            user = CustomUser.objects.get(pk=user_id)

            # Verificar si hay stock disponible
            if book.stock_quantity <= 0:
                return Response({'error': 'No hay ejemplares disponibles'}, status=400)

            # Crear el préstamo
            loan = BookLoan.objects.create(
                book=book,
                user=user,
                due_date=due_date
            )

            # Reducir el stock
            book.stock_quantity -= 1
            book.save()

            serializer = BookLoanSerializer(loan)
            return Response(serializer.data, status=201)

        except Book.DoesNotExist:
            return Response({'error': 'Libro no encontrado'}, status=404)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)


class DashboardStatsView(APIView):
    def get(self, request):
        # Estadísticas básicas
        total_books = Book.objects.count()
        active_users = CustomUser.objects.count()

        # Estadísticas de préstamos
        active_loans = BookLoan.objects.filter(status='active').count()
        overdue_loans = BookLoan.objects.filter(status='overdue').count()
        returned_loans = BookLoan.objects.filter(status='returned').count()
        lost_books = BookLoan.objects.filter(status='lost').count()
        total_loans = BookLoan.objects.count()

        # Calcular libros disponibles
        total_stock = sum(book.stock_quantity for book in Book.objects.all())
        books_available = total_stock

        # Estadísticas por rol de usuario
        students = CustomUser.objects.filter(role='student').count()
        librarians = CustomUser.objects.filter(role='librarian').count()

        return Response({
            'total_books': total_books,
            'active_users': active_users,
            'students': students,
            'librarians': librarians,
            'active_loans': active_loans,
            'overdue_loans': overdue_loans,
            'returned_loans': returned_loans,
            'lost_books': lost_books,
            'total_loans': total_loans,
            'books_available': books_available
        })


class ReturnBookView(APIView):
    def post(self, request, loan_id):
        try:
            loan = BookLoan.objects.get(pk=loan_id)

            if loan.status != 'active' and loan.status != 'overdue':
                return Response({'error': 'Este préstamo ya no está activo'}, status=400)

            result = loan.return_book()

            serializer = BookLoanSerializer(loan)
            return Response({
                'loan': serializer.data,
                'return_info': result
            }, status=200)

        except BookLoan.DoesNotExist:
            return Response({'error': 'Préstamo no encontrado'}, status=404)


class MarkBookAsLostView(APIView):
    def post(self, request, loan_id):
        try:
            loan = BookLoan.objects.get(pk=loan_id)

            if loan.status != 'active' and loan.status != 'overdue':
                return Response({'error': 'Este préstamo ya no está activo'}, status=400)

            result = loan.mark_as_lost()

            serializer = BookLoanSerializer(loan)
            return Response({
                'loan': serializer.data,
                'lost_info': result
            }, status=200)

        except BookLoan.DoesNotExist:
            return Response({'error': 'Préstamo no encontrado'}, status=404)


class ActivityFeedView(APIView):
    def get(self, request):
        # Obtener todos los préstamos ordenados por fecha de creación
        loans = BookLoan.objects.all().order_by('-created_at')

        activities = []

        for loan in loans:
            user_name = f"{loan.user.first_name} {loan.user.last_name}"
            book_title = loan.book.title

            # Determinar la acción basada en el estado
            if loan.status == 'active':
                action = 'borrowed'
                action_display = 'Borrowed'
                icon = '📖'
            elif loan.status == 'returned':
                action = 'returned'
                action_display = 'Returned'
                icon = '✅'
                # Verificar si fue tardío
                if loan.return_date and loan.return_date > loan.due_date:
                    icon = '⏰'
                    action_display = 'Returned Late'
            elif loan.status == 'lost':
                action = 'lost'
                action_display = 'Lost'
                icon = '❌'
            elif loan.status == 'overdue':
                action = 'overdue'
                action_display = 'Overdue'
                icon = '⚠️'
            else:
                continue

            # Calcular días de retraso si aplica
            is_late = False
            days_late = 0
            if loan.status == 'returned' and loan.return_date and loan.return_date > loan.due_date:
                is_late = True
                days_late = (loan.return_date - loan.due_date).days

            activity = {
                'id': loan.id,
                'user_name': user_name,
                'book_title': book_title,
                'action': action,
                'action_display': action_display,
                'icon': icon,
                'timestamp': loan.created_at if action == 'borrowed' else loan.updated_at,
                'is_late': is_late,
                'days_late': days_late
            }

            activities.append(activity)

        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data)


class MyLoansView(APIView):
    def get(self, request):
        # Obtener el usuario desde el token JWT
        user = request.user

        # Filtrar préstamos del usuario actual
        loans = BookLoan.objects.filter(user=user).order_by('-loan_date')

        # Actualizar estados automáticamente
        for loan in loans:
            loan.update_status()

        serializer = MyLoanSerializer(loans, many=True)
        return Response(serializer.data)
