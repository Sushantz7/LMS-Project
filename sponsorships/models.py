from django.db import models
from users.models import CustomUser
from django.utils import timezone
from courses.models import Course
from django.contrib.auth import get_user_model

User=get_user_model()

class Sponsorship(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    sponsor = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='sponsored_students',
        limit_choices_to={'role': 'sponsor'}
    )
    student = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='sponsorships',
        limit_choices_to={'role': 'student'}
    )
    funding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    funded_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.sponsor.username} -> {self.student.username} (${self.funding_amount})"

class SponsorshipRequest(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} → {self.course.title} ({self.status})"
