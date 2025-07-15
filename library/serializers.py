from rest_framework import serializers
from .models import Book, CustomUser, BookLoan

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']

    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data, username=validated_data['email'])
        user.set_unusable_password()
        user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'email', 'role', 'date_joined']


class BookLoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = BookLoan
        fields = ['id', 'book', 'book_title', 'book_author', 'user', 'user_name', 'user_email', 'loan_date', 'due_date', 'return_date', 'status']
        read_only_fields = ['id', 'loan_date', 'return_date', 'status']


class MyLoanSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_author = serializers.CharField(source='book.author', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()

    class Meta:
        model = BookLoan
        fields = ['id', 'book_title', 'book_author', 'loan_date', 'due_date', 'return_date', 'status', 'is_overdue', 'days_remaining']
        read_only_fields = ['id', 'loan_date', 'return_date', 'status']

    def get_is_overdue(self, obj):
        return obj.is_overdue()

    def get_days_remaining(self, obj):
        from django.utils import timezone
        if obj.status == 'active':
            days = (obj.due_date - timezone.now()).days
            return max(0, days) if days > 0 else abs(days)
        return 0


class ActivitySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    user_name = serializers.CharField()
    book_title = serializers.CharField()
    action = serializers.CharField()  # 'borrowed', 'returned', 'lost'
    action_display = serializers.CharField()
    icon = serializers.CharField()
    timestamp = serializers.DateTimeField()
    is_late = serializers.BooleanField(default=False)
    days_late = serializers.IntegerField(default=0)
