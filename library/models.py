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



