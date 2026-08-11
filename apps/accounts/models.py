from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    email = models.EmailField(unique=True)

    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)

    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=255)
    national_code = models.CharField(max_length=20, blank=True, null=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return self.full_name or self.user.email
    
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    title = models.CharField(max_length=100)  # خانه، محل کار و...
    full_name = models.CharField(max_length=255)

    phone = models.CharField(max_length=15)

    province = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    address_line = models.TextField()
    postal_code = models.CharField(max_length=20)

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.email}"