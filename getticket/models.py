from django.db import models
from django.contrib.auth.models import User


# ---------------- Ticket Transfer Request ----------------
class TicketTransferRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Passenger (who requests transfer)
    passenger_name = models.CharField(max_length=100)
    train_number = models.CharField(max_length=20)
    journey_date = models.DateField()
    seat_number = models.CharField(max_length=10)
    transferred_to = models.CharField(max_length=100)

    # File upload (PDF, DOC, etc.)
    ticket_file = models.FileField(upload_to="tickets/files/", blank=True, null=True)

    # Image upload (JPG, PNG)
    ticket_image = models.ImageField(upload_to="tickets/images/", blank=True, null=True)

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    remark = models.TextField(blank=True, null=True)  # ✅ remark saved by staff
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.passenger_name} ➜ {self.transferred_to} ({self.status})"


# ---------------- Railway Staff Profile ----------------
class RailwayStaff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hrms_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100, default="General")
    role = models.CharField(
        max_length=50,
        choices=[
            ("HEAD", "Ticket Booking Head"),
            ("CLERK", "Clerk"),
            ("OTHER", "Other"),
        ],
        default="OTHER",
    )

    def __str__(self):
        return f"{self.user.username} - {self.hrms_id} ({self.role})"
