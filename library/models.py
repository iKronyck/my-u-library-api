from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser


class Book(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    title = models.CharField(max_length=200, verbose_name="Title")
    author = models.CharField(max_length=100, verbose_name="Author")
    published_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(2024)
        ],
        verbose_name="Published Year"
    )
    genre = models.CharField(max_length=50, verbose_name="Genre")
    stock_quantity = models.IntegerField(
        validators=[MinValueValidator(0)],
        verbose_name="Stock Quantity"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book"
        verbose_name_plural = "Books"
        ordering = ['title']

    def __str__(self):
        return f"{self.title} by {self.author}"

    def is_available(self):
        """Check if the book is available in stock"""
        return self.stock_quantity > 0

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('librarian', 'Librarian'),
    )

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    password = models.CharField(max_length=128, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.role})"


class BookLoan(models.Model):
    LOAN_STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
        ('lost', 'Lost'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='loans')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='loans')
    loan_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=LOAN_STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Book Loan"
        verbose_name_plural = "Book Loans"
        ordering = ['-loan_date']

    def __str__(self):
        return f"{self.book.title} - {self.user.email} ({self.status})"

    def is_overdue(self):
        """Check if the loan is overdue"""
        from django.utils import timezone
        return self.status == 'active' and timezone.now() > self.due_date

    def update_status(self):
        """Update loan status based on current date and due date"""
        from django.utils import timezone
        now = timezone.now()

        if self.status == 'active' and now > self.due_date:
            self.status = 'overdue'
            self.save()
        return self.status

    def return_book(self):
        """Mark book as returned and update stock"""
        from django.utils import timezone

        # Verificar si está vencido
        is_late = timezone.now() > self.due_date

        self.status = 'returned'
        self.return_date = timezone.now()
        self.save()

        # Aumentar stock del libro
        self.book.stock_quantity += 1
        self.book.save()

        return {
            'status': 'returned',
            'is_late': is_late,
            'days_late': (timezone.now() - self.due_date).days if is_late else 0
        }

    def mark_as_lost(self):
        """Mark book as lost"""
        self.status = 'lost'
        self.save()
        return {'status': 'lost'}



