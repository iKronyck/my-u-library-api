from rest_framework import serializers
from .models import Book, CustomUser

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
