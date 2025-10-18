from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth import get_user_model
class CustomUser(AbstractUser):
    USER_TYPE_CHOICE = (
        ('user', 'User'),
        ('owner', 'Owner'),
        ('mechanic','Mechanic'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICE, default='user')
    phone = models.CharField(max_length=15, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, blank=True)
    zip = models.CharField(max_length=6, blank=True)

    def __str__(self):
        return self.username


User = get_user_model()

class AddBunker(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    bunker_name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    slots = models.PositiveIntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='bunker_images/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.bunker_name
    



class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bunker = models.ForeignKey(AddBunker, on_delete=models.CASCADE, related_name='bookings')

    vehicle_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=15)  # 🔹 Added this line
    booking_date = models.DateField()
    time_slot = models.PositiveIntegerField()  # in hours

    booked_at = models.DateTimeField(auto_now_add=True)

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('done', 'Done'),
        ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.bunker.bunker_name} ({self.booking_date})"

    class Meta:
        ordering = ['-booked_at']

class Mechanic(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mechanics')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mechanic_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    experience = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name